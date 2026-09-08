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

  2. IL POUSSE vers la note iCloud de l'agent (dossier « agents »), que le commanditaire
     lit depuis son iPhone.

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
import sys, os, re, json, subprocess, pathlib, hashlib, datetime, time, unicodedata
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
            # La ligne de réouverture est de la MÉCANIQUE : elle n'a rien à
            # faire dans ce que lit le commanditaire, qui est CEO. Elle porte
            # une commande shell — exactement ce que la consigne interdit.
            if not l.lstrip().startswith("↻"):
                courant.append(l.strip())
        elif not l.strip():
            courant = None
    out = []
    for b in blocs:
        # Les lignes de continuation d'un libellé se recollent — un titre en
        # gras court souvent sur deux lignes. Mais une ligne de RÉPONSE
        # (`oui → …`) garde la sienne : sur un téléphone, trois réponses
        # aplaties en un paragraphe redeviennent le pavé qu'on veut éviter.
        t = b[0]
        for l in b[1:]:
            t += ("\n" if REPONSE.match(l) else " ") + l
        t = re.sub(r"!(haut|moyen|bas)\b", "", t, flags=re.I)
        t = re.sub(r"(?:^|(?<=\s))@[A-Za-zÀ-ÿ][\w-]*\b", "", t)
        t = CONSTAT.sub("", t)      # `?constat` est un marqueur, pas du texte
        out.append(t)
    return out


# ── LES CONSTATS ─────────────────────────────────────────────────────────
# Un `todo.md` mélange deux natures que rien ne distinguait :
#
#   une TÂCHE      « construire ceci »  reste vraie jusqu'à ce qu'on la fasse
#   un CONSTAT     « ceci manque »      peut cesser d'être vrai TOUT SEUL
#
# Trouvé par Splide PO le 07/09/2026 : sur seize points remis au commanditaire,
# cinq étaient faux — et les deux plus coûteux n'étaient pas des oublis, mais
# des constats mesurés proprement, datés, devenus faux deux jours plus tard sans
# que rien ne le signale. Un constat bien mesuré n'est pas plus DURABLE qu'un
# constat bâclé : seulement plus crédible, donc plus dangereux quand il périme.
#
# Le hook ne peut pas savoir si un constat est vrai. Il peut exiger qu'il porte
# de quoi le rouvrir, et rejouer cette vérification au seul moment qui compte —
# celui où le constat PART vers le commanditaire.
#
# LE MARQUEUR VIT DANS LE LIBELLÉ, et c'est ce qui rend l'ajout gratuit : le
# dialecte est lu par quatre programmes, dont trois portent leur propre copie de
# l'expression qui décode une ligne. Ces trois-là capturent la case et le
# libellé EN BLOC — `?constat`, comme `!haut` et `@user` avant lui, leur est
# invisible par construction.
# Une ligne de réponse : « oui → … », « 2 → … ». Le libellé court à gauche de
# la flèche est la réponse que le commanditaire donnera ; ce qui suit est ce
# qu'elle DÉCLENCHE. Deux au moins, sinon ce n'est pas une question fermée.
REPONSE = re.compile(r"^\s*\S[^→\n]{0,24}?\s*→\s*\S", re.M)

CONSTAT = re.compile(r"(?:^|(?<=\s))\?constat\b", re.I)
# `↻ machine|service :: commande :: motif attendu`
#   La SOURCE est déclarée parce qu'elle est le second échec de PO : son
#   contrôle décodait un cache local vieux de quatre jours au lieu d'interroger
#   le service. Chiffre net, cohérent, reproductible — et hors sujet. Une mesure
#   locale ne répond jamais à une question distante ; l'écrire oblige à y penser.
REOUVRE = re.compile(r"^\s*↻\s*(machine|service)\s*::\s*(.+?)\s*::\s*(.+?)\s*$",
                     re.I | re.M)

TIENT, TOMBE, MUET = "TIENT", "TOMBÉ", "MUET"
# Bornes dures : ce hook a 40 s avant d'être tué, et un tour qui pend est pire
# qu'un constat périmé. Rejouer cent fois par jour ne rend pas un constat vrai —
# ça reproduit cent fois la même erreur avec une confiance croissante.
CONSTAT_MAX, CONSTAT_S, CONSTAT_BUDGET = 5, 10, 25


def blocs_lignes(texte):
    """Les blocs de tâches, lignes BRUTES — marqueurs compris.

    `blocs_bruts()` recolle et nettoie pour l'affichage ; ici on a besoin du
    texte tel qu'écrit, sinon la ligne `↻` disparaît avec le reste."""
    blocs, courant = [], None
    for l in texte.splitlines():
        if re.match(r"^\s*[-*]\s*\[( |x|X|>|~)\]\s+", l):
            courant = [l]
            blocs.append(courant)
        elif courant is not None and l.strip() and re.match(r"^\s+\S", l):
            courant.append(l)
        elif not l.strip():
            courant = None
    return ["\n".join(b) for b in blocs]


def specs_constat(texte):
    """Par tâche, dans l'ordre : None, ou ce qu'il faut pour la rouvrir."""
    out = []
    for b in blocs_lignes(texte):
        if not CONSTAT.search(b):
            out.append(None)
            continue
        m = REOUVRE.search(b)
        out.append({"source": m.group(1).lower(), "cmd": m.group(2),
                    "motif": m.group(3)} if m else {"sans": True})
    return out


def rejouer(spec, budget):
    """TIENT · TOMBÉ · MUET — et jamais autre chose.

    MUET est la trouvaille de PO et le cœur du dispositif : **un contrôle qui
    n'aboutit pas ne doit JAMAIS se lire comme un constat confirmé.** Ça a servi
    dès son premier essai — ses mesures répétées ont déclenché la limitation de
    débit du site, et le contrôle a rendu MUET au lieu d'annoncer quatre routes
    cassées."""
    if budget <= 0:
        return MUET, "budget de temps épuisé"
    try:
        r = subprocess.run(["bash", "-c", spec["cmd"]], capture_output=True,
                           text=True, timeout=min(CONSTAT_S, budget))
    except subprocess.TimeoutExpired:
        return MUET, "la vérification n'a pas répondu à temps"
    except Exception as e:
        return MUET, "la vérification n'a pas pu être lancée (%s)" % type(e).__name__
    if r.returncode == 127:
        return MUET, "la commande de vérification n'existe pas"
    sortie_ = (r.stdout or "") + (r.stderr or "")
    try:
        trouve = re.search(spec["motif"], sortie_, re.I | re.S) is not None
    except re.error:
        trouve = spec["motif"].strip() in sortie_
    return (TIENT, "") if trouve else (TOMBE, "la vérification dit le contraire")


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
# L'INVERSE — retrouver la priorité d'un rappel DÉJÀ posé. Rappels n'expose
# aucun rang d'affichage : la pastille du titre est la seule trace de priorité
# qu'on puisse relire sans rouvrir le todo.
PASTILLE_RANG = {v: k for k, v in PASTILLE.items()}
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
          -- PAS DE `flagged`. Il a été posé sur les urgences le 07/09/2026 pour
          -- offrir une vue transversale via la liste « Signalés », puis retiré le
          -- jour même : le commanditaire a activé « Trier par ▸ Priorité » dans
          -- l'app, et la liste se range d'elle-même. Un drapeau qui double un tri
          -- déjà bon n'est plus un signal, c'est du bruit — et le drapeau
          -- appartient au lecteur, pas à l'agent : il doit rester libre de
          -- marquer ce qui compte POUR LUI.
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
                    "- [ ] !haut @user **J'autorise le paiement en ligne ? oui / non**\n"
                    "      oui → la boutique encaisse dès lundi ; il me faut ta "
                    "signature, 20 min.\n"
                    "      non → on ouvre sans encaissement, les clients paient "
                    "à la livraison.\n"
                    "      Ça attend depuis 4 jours ; j'ai continué sur le reste.\n\n"
                    "UNE QUESTION FERMÉE, JAMAIS UN CONSTAT. Un constat lui laisse "
                    "tout le travail : comprendre ce qu'on lui demande, deviner "
                    "comment répondre, et mesurer seul ce qu'il risque à ne pas "
                    "répondre. Il doit trancher d'un mot, depuis son téléphone, "
                    "sans rien ouvrir.\n\n"
                    "Sous la ligne, une ligne par réponse possible — ce qu'elle "
                    "DÉCLENCHE, pas ce qu'elle signifie. Trois voies : numérote-les, "
                    "il répond « 2 ». Et si tu ne sais pas quoi faire de l'une des "
                    "réponses, la question n'est pas prête : elle n'a rien à faire "
                    "dans sa liste.\n\n"
                    "Le commanditaire est CEO — PAS de nom de fichier, de "
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
        t["_i"] = i
        attente.append(t)

    # --- 2 bis. LES CONSTATS : rouvrir avant de servir -----------------------
    # Ici et nulle part ailleurs. Le hook tire à chaque fin de tour ; un contrôle
    # réseau coûte des secondes. Le bon instant est celui où le constat ATTEINT
    # le commanditaire — c'est rare, et c'est exactement le moment qui a échoué.
    specs = specs_constat(texte)
    manquants = [t for t in attente
                 if t["_i"] < len(specs) and (specs[t["_i"]] or {}).get("sans")]
    if manquants:
        # Même garde anti-boucle que la règle 1 : au plus un blocage par état du
        # todo. Un agent ne doit JAMAIS pouvoir être coincé par ce hook.
        sig = hashlib.sha1(("constat|%s|%d" % (empreinte, len(manquants)))
                           .encode()).hexdigest()[:16]
        temoin = ETAT / ("%s.constat" % session)
        if not (temoin.exists() and temoin.read_text().strip() == sig):
            temoin.write_text(sig)
            sortie(2,
                "attente : %d constat(s) sans moyen d'être rouvert(s) : %s.\n\n"
                "Un constat n'est pas une tâche. « Construire X » reste vrai "
                "jusqu'à ce que tu le fasses ; « X manque » peut cesser d'être "
                "vrai TOUT SEUL, sans que personne y touche — et un constat bien "
                "mesuré n'est pas plus durable qu'un constat bâclé, seulement "
                "plus crédible, donc plus dangereux quand il périme.\n\n"
                "Ajoute sous chaque ligne `?constat` de quoi la rejouer :\n\n"
                "      ↻ service :: curl -s -o /dev/null -w '%%{http_code}' "
                "https://exemple.fr/contact :: ^200$\n\n"
                "Trois champs. D'ABORD LA SOURCE — `machine` si la réponse est "
                "sur ce poste, `service` si elle est chez le fournisseur. Une "
                "mesure locale ne répond jamais à une question distante : c'est "
                "ainsi qu'un contrôle a décodé un cache vieux de quatre jours et "
                "rendu un chiffre net, cohérent, et hors sujet. Puis la commande, "
                "puis ce qu'elle doit répondre si le constat tient encore.\n\n"
                "Si une ligne est une tâche et non un constat, retire `?constat`."
                % (len(manquants), ", ".join(t["titre"][:40] for t in manquants[:3])))

    tombes, restant = [], CONSTAT_BUDGET
    for t in [x for x in attente if x["_i"] < len(specs) and specs[x["_i"]]
              and not specs[x["_i"]].get("sans")][:CONSTAT_MAX]:
        t0 = time.time()
        verdict, raison = rejouer(specs[t["_i"]], restant)
        restant -= time.time() - t0
        jour = datetime.date.today().strftime("%d/%m")
        if verdict == TIENT:
            t["corps"] = (t.get("corps") or "") + " · reconfirmé le %s" % jour
        elif verdict == MUET:
            # JAMAIS lu comme une confirmation : le constat part quand même, en
            # disant que la vérification n'a pas abouti.
            t["corps"] = (t.get("corps") or "") + " · le %s, %s" % (jour, raison)
        else:
            t["_tombe"] = True
            tombes.append(t["titre"])

    # LE CONSTAT TOMBÉ QUITTE LES RAPPELS — ET RESTE DANS LE TODO DE L'AGENT.
    # Le commanditaire ne veut pas de lignes à contrôler ; sa liste doit donc
    # raccourcir toute seule. Mais AUCUN verdict de machine ne détruit quoi que
    # ce soit : une vérification qui se trompe effacerait un vrai blocage en
    # silence, et un contrôle dont l'échec ressemble au succès est précisément
    # la panne que tout ce dispositif traque. L'agent tranche, au tour suivant.
    attente = [t for t in attente if not t.get("_tombe")]

    # --- 2 ter. LA FORME : une question, jamais un constat -------------------
    # Le hook connaît la forme mieux qu'un texte de socle : il lit ces lignes à
    # chaque fin de tour, il sait donc les refuser AU MOMENT où elles sont
    # écrites, à UN agent, au lieu de faire relire quinze lignes de consignes à
    # douze agents à chaque démarrage. Une règle écrite est un conseil ; une
    # règle ici est appliquée.
    #
    # IL NE JUGE QUE LA FORME, jamais la qualité : il voit qu'il manque un point
    # d'interrogation et des réponses, il ne saura jamais distinguer une bonne
    # question d'une mauvaise. C'est pour ça que les deux lignes du socle
    # restent nécessaires.
    empreintes = {hashlib.sha1(t["titre"].encode("utf-8", "replace")).hexdigest()[:12]
                  for t in attente}
    vus_f = ETAT / ("%s.forme" % re.sub(r"[^A-Za-z0-9_-]", "-", agent))
    if not vus_f.exists():
        # PREMIÈRE RENCONTRE : on enregistre l'arriéré SANS bloquer. Reprendre
        # 73 lignes anciennes n'est pas le travail du tour en cours, et un
        # garde-fou qui bloque tout le monde le premier jour est un garde-fou
        # qu'on finit par désarmer — la leçon du faux positif du 05/09.
        vus_f.write_text("\n".join(sorted(empreintes)))
    else:
        deja = set(vus_f.read_text().split())
        mauvais = [t for t in attente
                   if hashlib.sha1(t["titre"].encode("utf-8", "replace")).hexdigest()[:12]
                   not in deja
                   and not ("?" in t["titre"]
                            and len(REPONSE.findall(t.get("corps") or "")) >= 2)]
        # ON N'AVERTIT QU'UNE FOIS PAR LIGNE, comme les rappels tranchés plus
        # haut : la ligne rejoint les vues même si elle est mal formée. Un hook
        # qui redemande à chaque tour finit par coincer l'agent, et aucun
        # dispositif ne doit pouvoir faire ça.
        vus_f.write_text("\n".join(sorted(deja | empreintes)))
        if mauvais:
            sortie(2,
                "attente : %d ligne(s) qui attend(ent) le commanditaire sont écrites "
                "comme des CONSTATS, pas comme des questions : %s.\n\n"
                "Un constat lui laisse tout le travail — comprendre ce qu'on lui "
                "demande, deviner comment répondre, mesurer seul ce qu'il risque "
                "à ne pas répondre. Il doit trancher d'un mot, depuis son "
                "téléphone, sans rien ouvrir.\n\n"
                "Réécris chacune dans cette forme :\n\n"
                "- [ ] !haut @user **J'autorise le paiement en ligne ? oui / non**\n"
                "      oui → la boutique encaisse dès lundi ; il me faut ta "
                "signature, 20 min.\n"
                "      non → on ouvre sans encaissement, les clients paient à la "
                "livraison.\n"
                "      Ça attend depuis 4 jours ; j'ai continué sur le reste.\n\n"
                "Le libellé porte la question ET les réponses possibles. Dessous, "
                "une ligne par réponse : ce qu'elle DÉCLENCHE, pas ce qu'elle "
                "signifie. Trois voies : numérote-les, il répond « 2 ».\n\n"
                "Et si tu ne sais pas quoi faire de l'une des réponses, la question "
                "n'est pas prête — elle n'a rien à faire dans sa liste.\n\n"
                "Je ne te le redemanderai pas pour ces lignes-là : c'est un "
                "avertissement, pas un blocage permanent."
                % (len(mauvais),
                   ", ".join("« %s »" % t["titre"][:50] for t in mauvais[:3])
                   + (", …" if len(mauvais) > 3 else "")))

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

    # --- 4. remettre l'ordre ------------------------------------------------
    # Rappels affiche dans l'ordre d'AJOUT, et son tri par priorité n'est pas
    # scriptable : vérifié le 07/09/2026, un rappel n'expose ni position ni rang
    # — name, body, priority, flagged, les dates, rien d'autre. Créer le premier
    # lot déjà trié ne suffit donc pas, et c'est le commanditaire qui l'a vu :
    # la demande urgente écrite aujourd'hui se range SOUS les demandes moyennes
    # d'hier. Mesuré sur une liste réelle — quatre 🔴 enterrés sous huit 🟠.
    #
    # Un rappel RECRÉÉ repart en fin de liste. On recrée donc ceux qui devraient
    # y être : est mal placé tout rappel suivi d'un rappel PLUS prioritaire.
    # Le budget est partagé avec la purge — chaque suppression coûte une requête
    # Apple Events (~2 s), et le hook entier tient dans 40 s.
    budget = 8 - len(aOter)
    if budget > 0:
        par_lib = {}
        for t in attente:
            par_lib[libelle_rappel(t["titre"], t["prio"])[:250]] = t
        ordre = [l for l in existants if l in voulus and not existants[l]]
        ordre += [c.split(SEP_CHAMP)[0] for c in aCreer]
        rangs = [RANG.get(PASTILLE_RANG.get(l[:1], "moyen"), 1) for l in ordre]
        # le plus prioritaire qui reste APRÈS chaque position
        apres = [9] * (len(rangs) + 1)
        for i in range(len(rangs) - 1, -1, -1):
            apres[i] = min(rangs[i], apres[i + 1])
        malPlaces = [ordre[i] for i in range(len(rangs)) if apres[i + 1] < rangs[i]]
        malPlaces = sorted(malPlaces, key=lambda l: RANG.get(PASTILLE_RANG.get(l[:1], "moyen"), 1))[:budget]
        if malPlaces:
            _osa(RAPPELS_SUPPRIMER, agent, SEP_LOT.join(malPlaces))
            refaits = []
            for lib in malPlaces:
                t = par_lib.get(lib)
                if not t:
                    continue
                refaits.append(SEP_CHAMP.join(
                    (lib, (t.get("corps") or "").replace(SEP_CHAMP, " ").replace(SEP_LOT, " "),
                     str(PRIO_APPLE.get(t["prio"], 5)))))
            if refaits:
                _osa(RAPPELS_ECRIRE, agent, SEP_LOT.join(refaits))

    dernier.write_text(empreinte)

    # --- 5. DIRE À L'AGENT CE QUI EST TOMBÉ ----------------------------------
    # Sans ça, un constat quitterait les Rappels sans que personne le sache, et
    # on aurait fabriqué la panne même qu'on traque : un effet sans trace. Le
    # constat est toujours dans le todo — c'est l'agent qui tranche, pas le
    # hook, parce qu'une vérification peut se tromper. Bornée par la même garde :
    # au plus un blocage par état du todo, jamais d'agent coincé.
    if tombes:
        sig = hashlib.sha1(("tombe|%s|%s" % (empreinte, "|".join(tombes)))
                           .encode()).hexdigest()[:16]
        temoin = ETAT / ("%s.tombe" % session)
        if not (temoin.exists() and temoin.read_text().strip() == sig):
            temoin.write_text(sig)
            sortie(2,
                "attente : %d constat(s) ne tiennent plus — leur propre "
                "vérification dit le contraire :\n\n%s\n\n"
                "Ils viennent de quitter les Rappels du commanditaire, pour qu'il "
                "n'ait pas à contrôler des lignes fausses. Ils sont TOUJOURS dans "
                "`.mind/todo.md` : rien n'a été détruit, parce qu'une vérification "
                "peut se tromper et qu'un contrôle dont l'échec ressemble au "
                "succès est exactement ce qu'on cherche à éviter.\n\n"
                "À toi de trancher : si le constat est bien caduc, coche-le ou "
                "retire la ligne. S'il tient encore, c'est ta VÉRIFICATION qui est "
                "fausse — corrige-la plutôt que le constat, et demande-toi d'abord "
                "de quelle source elle a lu sa réponse."
                % (len(tombes), "\n".join("  ✗ " + t for t in tombes)))

    sortie()


if __name__ == "__main__":
    main()
