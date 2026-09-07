#!/usr/bin/env python3
"""attente - hook Stop. Ce qui attend le commanditaire, à chaque fin de tour.

POURQUOI CE HOOK EXISTE. `.mind/todo.md` était réclamé par `mind-guard`, un
`PreToolUse` armé sur `git commit`. Mesuré le 06/09/2026 : un agent qui analyse,
qui est bloqué maintenant, ou qui n'a pas encore commité n'écrivait donc RIEN.
Ce qui attendait le commanditaire n'arrivait qu'au prochain commit, parfois jamais — et
124 demandes s'étaient accumulées sur 10 projets sans qu'aucune ne remonte.

`Stop` est documenté « When Claude finishes responding » : une fois par tour, au
moment où l'agent rend la main. C'est le seul instant qui coïncide avec « Le commanditaire
va peut-être lire ».

DEUX CHOSES, DANS CET ORDRE :

  1. IL BLOQUE (code de sortie 2, « Prevents Claude from stopping ») si du code
     projet a bougé sans que `.mind/todo.md` suive. L'agent est renvoyé au
     travail : il ne peut pas rendre la main en ayant enterré un blocage dans
     un récap. C'est une contrainte mécanique, pas une consigne de prose — la
     prose, on a mesuré qu'elle ne suffisait pas.

  2. IL POUSSE vers le canal du commanditaire — par défaut la liste de rappels
     du système, une par agent, qu'il lit depuis son téléphone. Le canal a
     d'abord été une note ; les cases à cocher n'y survivaient pas à
     l'écriture, et une liste de rappels en offre de vraies. C'est ce qui
     rend la boucle bidirectionnelle : cocher une entrée renvoie la décision
     à l'agent.

FAIL-OPEN PARTOUT, ET SILENCIEUX. Un hook de reporting ne doit jamais empêcher
de travailler : toute erreur, tout doute, tout projet hors harnais sort en 0.
Le seul code 2 est celui de la règle 1, et il est borné par la garde
anti-boucle ci-dessous.

LA GARDE ANTI-BOUCLE EST OBLIGATOIRE. `Stop` se redéclenche après le tour que
le blocage a provoqué. Sans garde, un agent qui n'obtempère pas — ou qui ne
peut pas — tourne à l'infini. On ne bloque donc QU'UNE FOIS par état du code :
la signature de l'état ayant causé le blocage est mémorisée, et si elle se
représente à l'identique, on laisse passer. Au pire, un rappel manqué ; jamais
un agent coincé.

CE HOOK NE PARSE PAS LE DIALECTE. `chantiers()` de `claude-projets` est le
lecteur de `todo.md` (`!haut`, `@user`, les états), et il est importé, jamais
recopié : deux lecteurs du même format divergent au premier changement.
"""
import sys, os, re, json, subprocess, pathlib, hashlib, datetime, unicodedata
import importlib.machinery, importlib.util

ETAT = pathlib.Path.home() / ".claude" / "attente"

# À QUI S'ADRESSE UNE DEMANDE. Le dialecte de `todo.md` écrit `@<qui>`, et le
# gabarit du starter livre `@user`. Un atelier qui emploie un autre nom — un
# prénom, un rôle — le déclare ici ou dans `ATTENTE_DESTINATAIRES`, séparé par
# des virgules. La comparaison se fait en minuscules, comme le parseur.
#
# NE PAS écrire un nom en dur dans ce fichier : il est partagé par tous les
# projets, et un hook qui ne reconnaît pas le destinataire ne remonte RIEN —
# sans le dire, puisqu'il est fail-open.
DESTINATAIRES = tuple(
    d.strip().lower()
    for d in os.environ.get("ATTENTE_DESTINATAIRES", "user").split(",")
    if d.strip()
) or ("user",)

def sortie(code=0, message=None):
    if message:
        sys.stderr.write(message)
    sys.exit(code)


def _import(chemin, nom):
    """Le pattern de `claude-cadrage` : on importe, on ne duplique pas."""
    chemin = pathlib.Path(chemin)
    if not chemin.exists():
        return None
    try:
        loader = importlib.machinery.SourceFileLoader(nom, str(chemin))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _git(args, cwd=None):
    try:
        return subprocess.run(["git"] + args, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=15,
                              cwd=cwd)
    except Exception:
        return None


def nom_agent(racine):
    """Le nom LISIBLE de l'agent — c'est un titre de note, pas un slug.

    `journal.suffixe_agent()` résout le même cas mais rend `-<projet>-OPS` : il
    nomme un fichier. Ici on veut « <projet> OPS », tel que le commanditaire l'a écrit et
    tel que l'app Claude l'affiche.
    """
    depart = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    p = pathlib.Path(depart).resolve()
    try:
        rel = p.relative_to(pathlib.Path(racine).resolve())
        if len(rel.parts) == 2 and rel.parts[0] == "agents":
            return rel.parts[1]          # multi-agents : « <projet> OPS »
    except (ValueError, OSError):
        pass
    return p.name                        # mono-agent : « <projet> »


def blocs_bruts(texte):
    """Le texte COMPLET de chaque tâche : la ligne qui porte la case, plus ses
    lignes de continuation indentées, recollées en un paragraphe.

    `chantiers()` ne rend que la ligne de la case — c'est son contrat, et il est
    bon : le dialecte tient sur cette ligne. Mais un libellé en gras court
    souvent sur deux lignes, et le POURQUOI d'un blocage vit dans les lignes du
    dessous. S'en tenir à la première ligne coupait les titres au milieu
    (« partage d'écran » / « actif.** L'audit du 24/08 »).

    On ne réinterprète RIEN ici : les marqueurs `!prio` et `@qui` sont retirés
    parce que `chantiers()` les a DÉJÀ lus et en fait foi. Ce module n'en tire
    aucune décision — il met en forme, le dialecte reste au parseur importé.
    """
    lignes, blocs, courant = texte.splitlines(), [], None
    for l in lignes:
        if re.match(r"^\s*[-*]\s*\[( |x|X|>|~)\]\s+", l):
            courant = [re.sub(r"^\s*[-*]\s*\[( |x|X|>|~)\]\s+", "", l).strip()]
            blocs.append(courant)
        elif courant is not None and l.strip() and re.match(r"^\s+\S", l):
            courant.append(l.strip())
        elif not l.strip():
            courant = None
    out = []
    for b in blocs:
        t = " ".join(b)
        t = re.sub(r"!(haut|moyen|bas)\b", "", t, flags=re.I)
        t = re.sub(r"(?:^|(?<=\s))@[A-Za-zÀ-ÿ][\w-]*\b", "", t)
        out.append(t)
    return out


def lisible(s):
    """Du Markdown vers ce que le commanditaire lit sur son iPhone."""
    s = s.replace("`", "").replace("**", "").replace("__", "")
    return re.sub(r"\s{2,}", " ", s).strip(" .,;—-")


def titre_et_corps(brut):
    """Sépare la demande de son explication.

    Le gras du libellé porte la demande — c'est la convention de tous les
    `todo.md` de l'atelier. Quand il manque, on retombe sur la première phrase :
    mieux vaut une coupe grossière qu'un titre de huit lignes.
    """
    m = re.match(r"\s*\*\*(.+?)\*\*\s*(.*)", brut, re.S)
    if m:
        return lisible(m.group(1)), lisible(m.group(2))
    t = lisible(brut)
    m = re.match(r"(.{15,110}?[.:])\s+(.+)", t, re.S)
    if m:
        return m.group(1).rstrip(".:"), m.group(2)
    return (t[:110], "") if len(t) <= 110 else (t[:110].rsplit(" ", 1)[0] + "…", t[110:])


def _osa(script, *args):
    try:
        r = subprocess.run(["osascript", "-"] + list(args), input=script,
                           capture_output=True, text=True, timeout=25)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


# UNE LISTE PAR AGENT, qui porte son nom — « CTO », « <projet> OPS ».
# La première version n'en faisait qu'une, « 🤖 Décisions », avec le nom de
# l'agent en tête de chaque titre. Le commanditaire a tranché pour une liste par agent, et
# il a raison : Rappels a déjà une vue « Tout » qui agrège, donc séparer ne
# coûte pas la vue d'ensemble, alors que fondre les dix perdait la séparation.
#
# Les GROUPES de listes, eux, ne sont pas scriptables : le dictionnaire de
# Rappels ne connaît que `account`, `list` et `reminder`, et le `container`
# d'une liste est en lecture seule. Un groupe se crée donc à la main, une fois,
# et les listes s'y rangent par glisser-déposer — comme le dossier `agents` des
# Notes.

# Apple : 0 aucune, 1 haute, 5 moyenne, 9 basse. La priorité du dialecte devient
# donc une VRAIE priorité, triable et filtrable dans l'app — pas un `!haut` en
# tête de libellé.
PRIO_APPLE = {"haut": 1, "moyen": 5, "bas": 9}

# La pastille se lit AVANT le texte, et c'est tout l'intérêt sur un téléphone :
# on trie du regard sans lire. Trois couleurs et pas quatre — le dialecte de
# `todo.md` n'a que trois priorités (`!haut`, `!moyen`, `!bas`), et « moyen » est
# aussi ce qu'on obtient sans marqueur : un quatrième rond promettrait une
# distinction que la source ne porte pas.
PASTILLE = {"haut": "🔴", "moyen": "🟠", "bas": "🟡"}
RANG = {"haut": 0, "moyen": 1, "bas": 2}

RAPPELS_LIRE = '''
on run argv
  set nomListe to item 1 of argv
  tell application "Reminders"
    if not (exists list nomListe) then return ""
    set sortie to ""
    repeat with r in (reminders of list nomListe)
      set etat to "0"
      if completed of r then set etat to "1"
      set sortie to sortie & etat & tab & (name of r) & linefeed
    end repeat
    return sortie
  end tell
end run
'''

# UN SEUL APPEL POUR TOUT LE LOT. Mesuré le 06/09/2026 : un `osascript` par
# rappel mettait 45 s pour 15 décisions — au-delà du timeout de 40 s du hook,
# donc tué en conditions réelles. Le coût n'est pas dans Rappels, il est dans le
# démarrage d'`osascript` et l'ouverture du pont Apple Events. On paie ça une
# fois, pas quinze.
SEP_LOT, SEP_CHAMP = "\x1e", "\x1f"

RAPPELS_ECRIRE = '''
on run argv
  set nomListe to item 1 of argv
  set charge to item 2 of argv
  set anciensDelims to AppleScript's text item delimiters
  tell application "Reminders"
    if not (exists list nomListe) then make new list with properties {name:nomListe}
    set l to list nomListe
    set AppleScript's text item delimiters to "\x1e"
    set lots to text items of charge
    set AppleScript's text item delimiters to anciensDelims
    set n to 0
    repeat with unLot in lots
      if (length of unLot) > 0 then
        set AppleScript's text item delimiters to "\x1f"
        set champs to text items of unLot
        set AppleScript's text item delimiters to anciensDelims
        if (count of champs) is 3 then
          make new reminder at l with properties {name:(item 1 of champs), body:(item 2 of champs), priority:((item 3 of champs) as integer)}
          set n to n + 1
        end if
      end if
    end repeat
    return (n as text)
  end tell
end run
'''

RAPPELS_SUPPRIMER = '''
on run argv
  set nomListe to item 1 of argv
  set charge to item 2 of argv
  set anciensDelims to AppleScript's text item delimiters
  tell application "Reminders"
    if not (exists list nomListe) then return "0"
    set AppleScript's text item delimiters to "\x1e"
    set aOter to text items of charge
    set AppleScript's text item delimiters to anciensDelims
    set n to 0
    -- PAR FILTRE NATIF, ET LES DEUX AUTRES FORMES ONT ÉTÉ ESSAYÉES LE
    -- 07/09/2026 — chacune échoue à sa manière, et aucune ne le dit :
    --
    --   `repeat with r in (reminders of list …)` + `delete r` : `delete`
    --   retire l'élément de la collection qu'on parcourt, les indices se
    --   décalent, et le parcours MEURT sur « Can't get item N of every
    --   reminder » (-1728) après la PREMIÈRE suppression.
    --
    --   `repeat with i … to 1 by -1` + `reminder i of list` : correct, mais
    --   chaque accès indexé est une requête Apple Events à part. Sur une
    --   vingtaine de rappels le script dépasse le `timeout=25` de `_osa`,
    --   qui rend alors `None` — on ne supprime qu'une partie du lot, et
    --   comme le hook est fail-open, ça ressemble à un succès.
    --
    -- `whose name is` laisse Reminders faire le travail en une passe : ni
    -- décalage d'indices, ni aller-retour par élément.
    repeat with unNom in aOter
      set cibles to (every reminder of list nomListe whose name is (unNom as text))
      set n to n + (count of cibles)
      delete cibles
    end repeat
    return (n as text)
  end tell
end run
'''


def libelle_rappel(titre, prio):
    """Une pastille, puis le titre. Le nom de l'agent n'y est pas : c'est celui
    de la liste, et le répéter mangerait la largeur de l'écran d'un téléphone."""
    return "%s %s" % (PASTILLE.get(prio, "🟠"), titre)


RAPPELS_ETAT = '''
on run argv
  set nomListe to item 1 of argv
  tell application "Reminders"
    if not (exists list nomListe) then return ""
    set anciensDelims to AppleScript's text item delimiters
    set AppleScript's text item delimiters to linefeed
    set faits to (name of (every reminder of list nomListe whose completed is true)) as text
    set ouverts to (name of (every reminder of list nomListe whose completed is false)) as text
    set AppleScript's text item delimiters to anciensDelims
    return faits & "\x1e" & ouverts
  end tell
end run
'''


def rappels_actuels(liste):
    """(titre -> coché) — le parcours COMPLET, réservé aux tours où le todo a
    changé : c'est le seul moment où l'on crée ou purge des rappels."""
    brut = _osa(RAPPELS_LIRE, liste)
    out = {}
    for l in (brut or "").splitlines():
        if "\t" in l:
            etat, titre = l.split("\t", 1)
            out[titre.strip()] = (etat.strip() == "1")
    return out


def rappels_etat(liste, cache_s=60):
    """Les seuls titres cochés, par un filtre AppleScript natif.

    DEUX MESURES, LE 06/09/2026, ET ELLES DÉCIDENT DE LA FORME. Boucler en
    AppleScript (`repeat with r in reminders`) coûtait 5,8 s par tour d'agent ;
    le filtre `whose completed is true` rend la même chose en 1,1 s. Et comme un
    agent enchaîne parfois plusieurs tours en une minute, le résultat est gardé
    `cache_s` secondes : on ne paie qu'une fois. Le prix de ce cache est un
    retour différé d'au plus une minute — sans commune mesure avec le temps que
    Le commanditaire met à décider.
    """
    cache = ETAT / ("coches-%s.cache" % re.sub(r"[^A-Za-z0-9_-]", "-", liste))
    try:
        if cache.exists() and (datetime.datetime.now().timestamp()
                               - cache.stat().st_mtime) < cache_s:
            return json.loads(cache.read_text())
    except (OSError, ValueError):
        pass
    brut = _osa(RAPPELS_ETAT, liste)
    if brut is None:
        return [], []
    faits, _, ouverts = brut.partition(SEP_LOT)
    val = ([l.strip() for l in faits.splitlines() if l.strip()],
           # SANS PASTILLE = ÉCRIT PAR L'UTILISATEUR. L'agent préfixe toujours ses
           # rappels d'un 🔴🟠🟡 ; un rappel qui n'en porte pas vient donc de
           # lui. C'est ce qui remplace le canal descendant que portaient les
           # notes, et en mieux : c'est la même surface, dans les deux sens.
           [l.strip() for l in ouverts.splitlines()
            if l.strip() and l.strip()[0] not in "🔴🟠🟡"])
    try:
        cache.write_text(json.dumps(val))
    except OSError:
        pass
    return val


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sortie()

    # Un sous-agent a son propre événement (`SubagentStop`) et n'a pas à
    # déclarer l'attente de son parent.
    if data.get("agent_type") or data.get("agent_id"):
        sortie()

    ici = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    r = _git(["rev-parse", "--show-toplevel"], cwd=str(ici))
    if not r or r.returncode != 0:
        sortie()                                    # pas un dépôt : rien à dire
    racine = pathlib.Path(r.stdout.strip())

    # EN MULTI-AGENTS, LES HOOKS SONT CEUX DU PROJET, appelés en `../../` :
    # `CLAUDE_PROJECT_DIR` vaut alors `<projet>/agents/<projet> OPS`, qui n'a pas de
    # `.claude/hooks/`. Chercher là uniquement rendait l'import muet — et comme
    # ce hook est fail-open, il n'aurait RIEN fait, sans le dire. On cherche donc
    # aussi à côté de ce fichier, puis à la racine du dépôt.
    mg = None
    for cand in (ici / ".claude" / "hooks" / "mind-guard.py",
                 pathlib.Path(__file__).resolve().parent / "mind-guard.py",
                 racine / ".claude" / "hooks" / "mind-guard.py"):
        mg = _import(cand, "mind_guard")
        if mg and hasattr(mg, "contexte") and hasattr(mg, "is_project_code"):
            break
        mg = None
    if not mg:
        sortie()
    try:
        lot, projet, _faits = mg.contexte()
    except Exception:
        sortie()

    todo = racine / lot / ".mind" / "todo.md"
    if not todo.exists():
        sortie()                                    # projet hors harnais

    # --- 1. bloquer si du travail est sorti sans être noté --------------------
    st = _git(["status", "--porcelain"], cwd=str(racine))
    code = []
    if st and st.returncode == 0:
        for l in st.stdout.splitlines():
            f = l[3:].strip().strip('"')
            if f and mg.is_project_code(f, lot, projet):
                p = racine / f
                if p.exists():
                    code.append(p)

    ETAT.mkdir(parents=True, exist_ok=True)
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(data.get("session_id") or "x"))[:64]

    if code:
        recent = max(p.stat().st_mtime for p in code)
        if todo.stat().st_mtime < recent:
            # Signature de l'ÉTAT, pas du tour : c'est elle qui borne la boucle.
            sig = hashlib.sha1(
                ("%.0f|%d" % (recent, len(code))).encode()).hexdigest()[:16]
            temoin = ETAT / ("%s.bloc" % session)
            if temoin.exists() and temoin.read_text().strip() == sig:
                pass          # déjà réclamé pour cet état — on ne coince pas
            else:
                temoin.write_text(sig)
                sortie(2,
                    "attente : tu as modifié du code (%s) sans mettre "
                    "`.mind/todo.md` à jour. Ce fichier est le SEUL endroit où "
                    "le commanditaire voit ce qui lui revient — il le lit depuis son "
                    "iPhone, pas dans cette conversation.\n\n"
                    "Avant de rendre la main : coche ce que tu as fini, et "
                    "écris ce qui l'attend, une entrée par blocage, dans cette "
                    "forme exacte :\n\n"
                    "- [ ] !haut @user **Autoriser le paiement en ligne**\n"
                    "      Sans ça la boutique ne peut pas encaisser ; toi seul "
                    "peux signer le contrat.\n"
                    "      J'ai continué sur le reste ; ça attend depuis 4 jours.\n\n"
                    "Trois choses et rien d'autre : ce que tu lui demandes, "
                    "pourquoi ce ne peut être que lui, ce qui se passe s'il ne "
                    "répond pas. Le commanditaire est CEO — PAS de nom de fichier, de "
                    "fonction ni de variable d'environnement.\n\n"
                    "Tu ne t'arrêtes pas pour autant : si tu peux avancer par un "
                    "chemin réversible, prends-le, note l'hypothèse, et continue."
                    % (", ".join(p.name for p in code[:4])
                       + (", …" if len(code) > 4 else "")))

    agent = nom_agent(racine)

    # --- 1 bis. CE QUE L'UTILISATEUR A TRANCHÉ REVIENT À L'AGENT --------------------
    # C'est la moitié qui manquait à tout le dispositif : un rappel coché est
    # une décision prise, et personne ne la redescendait. On la lit à chaque
    # tour — même quand le todo n'a pas bougé — et on renvoie l'agent au
    # travail pour qu'il la traite. Bornée par la même garde anti-boucle : au
    # plus un rappel par état, jamais d'agent coincé.
    coches, demandes = rappels_etat(agent)
    if coches:
        vus = ETAT / ("%s.tranche" % re.sub(r"[^A-Za-z0-9_-]", "-", agent))
        deja = set(vus.read_text().splitlines()) if vus.exists() else set()
        neufs = [t for t in coches if t not in deja]
        if neufs:
            vus.write_text("\n".join(sorted(set(coches) | deja)))
            sortie(2,
                "attente : Le commanditaire a tranché %d point(s) depuis ses Rappels.\n\n%s\n\n"
                "Ouvre le rappel pour lire sa réponse s'il en a écrit une dans le "
                "corps, applique la décision, puis coche la tâche correspondante "
                "dans `.mind/todo.md` (`- [x]`). Si tu ne peux pas l'appliquer "
                "maintenant, dis-le dans le todo — mais ne la laisse pas ouverte "
                "sans trace : de son côté, il l'a considérée comme réglée."
                % (len(neufs), "\n".join("  ✓ " + t for t in neufs)))

    # --- 1 ter. CE QUE L'UTILISATEUR TE DEMANDE, LUI -------------------------------
    # Un rappel sans pastille est de sa main : il a écrit dans ta liste depuis
    # son téléphone. C'est le canal descendant, celui que portait le dossier
    # `<projet>` de ses notes. On ne bloque qu'une fois par demande.
    if demandes:
        vus = ETAT / ("%s.demandes" % re.sub(r"[^A-Za-z0-9_-]", "-", agent))
        deja = set(vus.read_text().splitlines()) if vus.exists() else set()
        neuves = [d for d in demandes if d not in deja]
        if neuves:
            vus.write_text("\n".join(sorted(set(demandes) | deja)))
            sortie(2,
                "attente : Le commanditaire t'a écrit %d demande(s) dans tes Rappels.\n\n%s\n\n"
                "Ouvre le rappel : le corps peut porter le détail. Traite-la, ou "
                "porte-la dans `.mind/todo.md` si elle demande du temps — puis "
                "COCHE le rappel pour lui dire que tu l'as prise. Ne le laisse pas "
                "sans réponse : de son côté, il ne sait pas si tu l'as vue."
                % (len(neuves), "\n".join("  → " + d for d in neuves)))

    # --- 2. composer ce qui attend le commanditaire ------------------------------------
    # 0,4 s par appel AppleScript, mesuré : trop pour être payé à chaque tour,
    # d'où la garde sur le `mtime` du todo.
    empreinte = "%.0f" % todo.stat().st_mtime
    dernier = ETAT / ("%s.pousse" % re.sub(r"[^A-Za-z0-9_-]", "-", agent))
    if dernier.exists() and dernier.read_text().strip() == empreinte:
        sortie()

    cp = _import(pathlib.Path.home() / ".local" / "bin" / "claude-projets",
                 "claude_projets")
    if not cp:
        sortie()
    try:
        texte = todo.read_text()
        taches = cp.chantiers(todo)     # le dialecte : prio, destinataire, état
        bruts = blocs_bruts(texte)      # le texte complet, pour la mise en forme
    except Exception:
        sortie()

    # Les deux listes décrivent les mêmes tâches dans le même ordre — même
    # motif de case, même fichier. Si elles divergent (todo réécrit entre les
    # deux lectures), on se rabat sur le libellé de `chantiers()` : tronqué,
    # mais jamais faux.
    attente = []
    for i, t in enumerate(taches):
        if t.get("qui") not in DESTINATAIRES or t.get("etat") != "afaire":
            continue
        t = dict(t)
        if i < len(bruts) and len(bruts) == len(taches):
            t["titre"], t["corps"] = titre_et_corps(bruts[i])
        else:
            t["titre"], t["corps"] = lisible(t["titre"]), ""
        attente.append(t)

    # --- 3. les Rappels : une vraie case à cocher par décision ---------------
    # LA NOTE ICLOUD A ÉTÉ RETIRÉE LE 06/09/2026, et c'est le commanditaire qui l'a vu :
    # dès lors que le rappel porte le titre, l'explication (son corps), la
    # priorité et une VRAIE case, la note ne faisait plus que dupliquer — avec
    # un rendu inférieur, puisque Notes force le corps à 11 px et ne sait pas
    # créer de case à cocher (styleType 100 au lieu de 103, lu dans
    # `NoteStore.sqlite`). Une surface unique, et deux qui ne peuvent plus
    # diverger. Ses notes existantes ne sont pas touchées : on n'y écrit plus.
    existants = rappels_actuels(agent)
    voulus, aCreer = set(), []
    # CRÉÉS DANS L'ORDRE D'IMPORTANCE. Rappels affiche par défaut dans l'ordre
    # d'ajout : créer en vrac mettait une décision urgente en bas de liste. Le
    # tri de l'app (Présentation ▸ Trier par ▸ Priorité) n'est pas scriptable —
    # aucune notion de tri dans son dictionnaire — donc on le prend de vitesse
    # en écrivant déjà trié.
    for t in sorted(attente, key=lambda x: RANG.get(x["prio"], 1)):
        lib = libelle_rappel(t["titre"], t["prio"])[:250]
        voulus.add(lib)
        if lib not in existants:
            aCreer.append(SEP_CHAMP.join(
                (lib, (t.get("corps") or "").replace(SEP_CHAMP, " ").replace(SEP_LOT, " "),
                 str(PRIO_APPLE.get(t["prio"], 5)))))
    if aCreer:
        _osa(RAPPELS_ECRIRE, agent, SEP_LOT.join(aCreer))

    # Ce qui a quitté le todo a été réglé : le rappel n'a plus lieu d'être. On ne
    # touche QUE les rappels de cet agent — jamais ceux d'un autre —, et jamais
    # un rappel coché : c'est la trace de sa décision, à lui de la ranger.
    # La liste n'appartient qu'à cet agent : plus besoin de filtrer sur un
    # préfixe. Un rappel coché n'est jamais purgé — c'est la trace de la
    # décision du commanditaire, à lui de la ranger.
    # NE PURGER QUE CE QUE L'AGENT A ÉCRIT — d'où le test sur la pastille. Sans
    # lui, un rappel écrit par le commanditaire (qui n'en porte pas, et n'est donc jamais
    # dans `voulus`) serait effacé au tour suivant : sa demande disparaîtrait
    # sans laisser de trace. Attrapé par le test du canal descendant.
    # BORNÉ PAR TOUR. Chaque nom coûte une requête Apple Events — ~2 s mesuré
    # le 07/09/2026 — et `_osa` coupe à 25 s : un lot de 18 rendait `None` après
    # avoir supprimé une partie, ce qui ressemble à un succès. En régime établi
    # la purge ne touche que ce que l'agent vient de régler, un à trois rappels ;
    # au-delà, c'est un rattrapage, et il se termine aux tours suivants.
    aOter = sorted(lib for lib, fait in existants.items()
                   if lib not in voulus and not fait and lib[:1] in "🔴🟠🟡")[:8]
    if aOter:
        _osa(RAPPELS_SUPPRIMER, agent, SEP_LOT.join(aOter))
    dernier.write_text(empreinte)
    sortie()


if __name__ == "__main__":
    main()
