#!/usr/bin/env python3
"""Lit les `.mind/` de tous les projets d'un atelier et en rend deux vues.

    agentic-team.py                          le rapport terminal — le DIAGNOSTIC
    agentic-team.py --html team.html         une page autonome — la VUE D'ÉQUIPE
    agentic-team.py --projet <nom>           un seul projet, en détail

**Une seule lecture, deux sorties.** Diagnostiquer un projet et voir l'atelier
entier, c'est le même travail : ouvrir `.mind/state.md` et `.mind/todo.md`, et
constater l'état du harnais autour. Séparer les deux outils, ce serait deux
analyseurs à tenir d'accord — et le jour où ils divergent, personne ne le voit.

**Strictement en lecture.** Ce script n'écrit que le fichier HTML qu'on lui
demande. Il ne touche à aucun projet : il dit ce qu'il faut lancer, il ne le
lance pas.

La page HTML est **autonome** : ni serveur, ni CDN, ni fichier joint. Elle
s'ouvre d'un double-clic sur n'importe quelle machine, y compris hors ligne.
"""
import argparse, datetime, html, json, pathlib, re, signal, subprocess, sys, time

# ── Le contrat de lecture. Il doit rester identique à celui du tableau de bord :
#    deux analyseurs qui divergent, c'est deux vérités et aucun signal.
ENTETE = re.compile(r"\s*---\s*\n(.*?)\n---\s*(\n|$)", re.S)
CHAMPS = ("maj", "cap", "sante", "jalon", "balle", "depuis", "attente", "suivant")
TACHE = re.compile(r"^\s*[-*]\s*\[( |x|X|>|~)\]\s+(.+?)\s*$")
ETATS = {" ": "afaire", "x": "fait", "X": "fait", ">": "encours", "~": "encours"}
PRIO = re.compile(r"!(haut|moyen|bas)\b")
# Destinataire : `@<qui>`, n'importe quel nom. `@dehors` est le seul réservé — il
# désigne une attente extérieure, que personne ici ne peut lever. Tout autre
# marqueur nomme la personne dont la décision manque.
# Générique à dessein : le dialecte n'a pas à porter le prénom de qui que ce
# soit pour être réutilisable. Un atelier qui écrit `@<prénom>` reste lu tel
# quel — c'est le template livré qui est neutre, pas le format.
# Le `@` doit ouvrir un mot — sinon `root@serveur` serait lu comme un
# destinataire nommé « serveur », et le mot disparaîtrait du titre affiché.
QUI = re.compile(r"(?:^|(?<=\s))@([A-Za-zÀ-ÿ][\w-]*)\b")
DEHORS = "dehors"
CHANTIERS = re.compile(r"^#{1,3}\s*chantiers\b.*$", re.I | re.M)

# Trois formes coexistent depuis le 04/09/2026. Ce script embarque sa propre
# résolution plutôt que d'importer `claude-projets` : il doit tourner sur une
# machine où l'outillage du poste n'est pas installé.
MIND_ATTENDU = ("state.md", "todo.md")
FACT_ATTENDU = ("base.md", "architecture.md", "stack.md", "rules.md")
MIND_ANCIEN = ("state.md", "todo.md", "stack.md", "architecture.md", "rules.md")


def forme(p):
    """(forme, etats) — `etats` liste les couples (nom d'agent, dossier `.mind/`).
    En mono le nom vaut None : l'agent EST le projet."""
    agents = p / "agents"
    etats = []
    if agents.is_dir():
        try:
            etats = [(d.name, d / ".mind") for d in sorted(agents.iterdir())
                     if (d / ".mind").is_dir()]
        except OSError:
            etats = []
    if etats:
        return "multi", etats
    return ("mono" if (p / ".fact").is_dir() else "ancienne"), [(None, p / ".mind")]
ANCIENS = ("charter.md", "business.md", "clients.md", "overview.md")
IGNORE = {"agentic-starter", "claude-starter", "cbascule"}

TIEDE_JOURS, PERIME_JOURS = 7, 28


def entete(texte):
    m = ENTETE.match(texte or "")
    if not m:
        return {}
    d = {}
    for ligne in m.group(1).splitlines():
        if ":" in ligne:
            k, _, v = ligne.partition(":")
            k = k.strip().lower()
            if k in CHAMPS:
                d[k] = v.strip()
    return d


def taches(texte):
    """Le fichier ENTIER, toutes sections confondues.

    Ne pas se borner à une section « Chantiers » : les fichiers réels
    s'organisent librement — « Attend une décision », « Outillage », « Technique ».
    Une version antérieure ne lisait que ce qui suivait un titre « Chantiers »
    et rendait donc **zéro tâche** sur des fichiers pleins, sans rien signaler.
    Le titre reste reconnu par compatibilité avec les anciens `pilotage.md`,
    qui bornaient réellement leur section."""
    if not texte:
        return []
    parts = CHANTIERS.split(texte)
    corps = parts[1] if len(parts) > 1 else texte
    out = []
    for ligne in corps.splitlines():
        t = TACHE.match(ligne)
        if not t:
            continue
        titre = t.group(2)
        p = PRIO.search(titre)
        q = QUI.search(titre)
        out.append({
            "etat": ETATS.get(t.group(1), "afaire"),
            "titre": PRIO.sub("", QUI.sub("", titre)).strip(" -—·"),
            "prio": p.group(1) if p else "",
            "qui": q.group(1) if q else "",
        })
    return out


def lis(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def fraicheur(maj, aujourdhui):
    """Trois états, jamais deux : à jour, tiède, périmé — ou illisible."""
    try:
        d = datetime.date.fromisoformat(maj)
    except (ValueError, TypeError):
        return "illisible", None
    j = (aujourdhui - d).days
    if j > PERIME_JOURS:
        return "perime", j
    if j > TIEDE_JOURS:
        return "tiede", j
    return "frais", j


def jauge(h):
    """Le compte de mémoire, dit selon la forme. « 2/5 » sur un projet migré
    serait un reproche faux : après migration `.mind/` n'en porte que deux."""
    if h["forme"] == "ancienne":
        return ".mind %d/5" % len(h["mind"])
    n = " · %d agent(s)" % len(h["agents"]) if h["agents"] else ""
    return ".fact %d/4 · .mind %d%s" % (len(h["fact"]), len(h["mind"]), n)


def harnais(p: pathlib.Path):
    """L'état du harnais autour de la mémoire — c'est ça, le diagnostic."""
    f, etats = forme(p)
    fait, cl = p / ".fact", p / ".claude"
    # Le dossier de mémoire se déduit de la FORME, jamais de la présence d'un
    # `docs/` : des projets non migrés en ont déjà un, plein de sorties de build.
    mem = (p / "docs") if f != "ancienne" else (p / ".memory")
    h = {
        "git": (p / ".git").is_dir(),
        "claude_md": (p / "CLAUDE.md").is_file(),
        "forme": f,
        "agents": [n for n, _ in etats if n],
        "fact": sorted(x.name for x in fait.glob("*.md")) if fait.is_dir() else [],
        "mind": sorted({x.name for _, m in etats if m.is_dir() for x in m.glob("*.md")}),
        "memory": mem.is_dir(),
        "hooks": sorted(f.name for f in (cl / "hooks").glob("*.py")) if (cl / "hooks").is_dir() else [],
        "logs": len(list((p / ".logs").glob("*.md"))) if (p / ".logs").is_dir() else 0,
        "anciens": [n for n in ANCIENS if (mem / n).is_file()],
        "montent": [n for n in ("state.md", "rules.md", "architecture.md")
                    if (mem / n).is_file()],
        "cable": False,
    }
    attendu = MIND_ANCIEN if h["forme"] == "ancienne" else MIND_ATTENDU
    h["manque"] = [n for n in attendu if n not in h["mind"]]
    h["surplus"] = [n for n in h["mind"] if n not in attendu]
    if h["forme"] != "ancienne":
        h["manque"] += [".fact/" + n for n in FACT_ATTENDU if n not in h["fact"]]
        h["surplus"] += [".fact/" + n for n in h["fact"] if n not in FACT_ATTENDU]
    # Le CLAUDE.md nomme-t-il `.mind/` ? C'est le seul lien entre le contexte de
    # démarrage de l'agent et sa mémoire. Mesuré le 03/09/2026 : sur huit
    # projets, sept le nommaient — et le seul qui ne le nommait pas est celui
    # dont l'agent s'est trompé sur ses propres outils. Les `@imports` comptent,
    # un CLAUDE.md d'une ligne qui importe un autre fichier reste valable.
    h["oriente"] = False
    if h["claude_md"]:
        vu, restants = set(), [p / "CLAUDE.md"]
        while restants and len(vu) < 8:
            f = restants.pop()
            if f in vu or not f.is_file():
                continue
            vu.add(f)
            t = lis(f)
            if ".mind" in t:
                h["oriente"] = True
                break
            for imp in re.findall(r"^@(\S+)", t, re.M):
                restants.append((f.parent / imp).resolve())

    # Les droits **appliqués**. Un droit en prose est un espoir ; un `deny` est
    # un fait. `bypassPermissions` sans aucun `deny` = rien n'est interdit.
    h["deny"], h["mode"], h["reglages"] = None, None, False
    reglages = cl / "settings.json"
    if reglages.is_file():
        h["reglages"] = True
        try:
            s = json.loads(lis(reglages))
            tout = json.dumps(s.get("hooks", {}))
            h["cable"] = "mind-guard" in tout and "journal" in tout
            h["briefing"] = "briefing" in tout
            perm = s.get("permissions", {}) or {}
            h["deny"] = perm.get("deny", []) or []
            h["mode"] = perm.get("defaultMode", "")
        except (ValueError, TypeError):
            pass
    h.setdefault("briefing", False)
    return h


def verdict(h):
    """Quoi lancer. Le script ne le lance pas — c'est une décision, pas un geste."""
    if not h["mind"] and not h["memory"] and not h["fact"]:
        return "neuf", "Aucune mémoire : cloner le starter puis `/project-init`."
    # Un `.fact/` sans aucun `.mind/` n'est pas un projet neuf : c'est un projet
    # déclaré dont AUCUN agent ne dit où il en est. Le confondre avec « aucune
    # mémoire » enverrait relancer `/project-init` sur un projet déjà monté.
    if h["fact"] and not h["mind"]:
        return "sans-agent", ("`.fact/` est là mais aucun agent ne se déclare : il "
                              "manque un `.mind/`, à la racine en mono-agent ou dans "
                              "`agents/<nom>/`.")
    if h["anciens"] or h["montent"]:
        quoi = ", ".join(h["anciens"] + h["montent"])
        return "ancien", ("Taxonomie d'avant le 02/09/2026 (%s) : `/agentic-upgrade`, "
                          "puis le TRI de mémoire à la main." % quoi)
    if h["manque"]:
        ou = "La mémoire du harnais" if h["forme"] != "ancienne" else "`.mind/`"
        return "incomplet", ("%s est incomplète (%s manque) : `/agentic-upgrade`."
                             % (ou, ", ".join(h["manque"])))
    if not h["hooks"]:
        return "sans-hooks", "Mémoire en place mais aucun hook : `/agentic-sync`."
    if not h["cable"]:
        return "non-cable", ("Hooks copiés mais absents de `settings.json` : les câbler. "
                             "Un hook non câblé ne fait rien et ne le dit pas.")
    if not h["git"]:
        return "sans-git", ("Hooks câblés mais pas de dépôt git : ils se déclenchent au "
                            "commit, donc ils sont inertes.")
    if h["surplus"]:
        combien = "quatre dans `.fact/` et deux dans `.mind/`" if h["forme"] != "ancienne" \
                  else "EXACTEMENT cinq dans `.mind/`"
        return "surplus", ("La mémoire porte %d fichier(s) de trop (%s) : le harnais en "
                           "tient %s." % (len(h["surplus"]), ", ".join(h["surplus"]), combien))
    if not h["oriente"]:
        return "aveugle", ("Le `CLAUDE.md` ne nomme jamais `.mind/` : rien dans le "
                           "contexte de démarrage ne dit à l'agent que sa mémoire "
                           "existe. Il répondra de mémoire propre, sans l'ouvrir.")
    if not h["briefing"]:
        return "sans-briefing", ("Aucun hook `briefing` câblé : l'agent doit penser à "
                                 "ouvrir `.mind/`. `/agentic-sync` le pose.")
    if not h["deny"]:
        return "sans-deny", ("Aucune règle `deny`%s : ce qui doit être interdit ici ne "
                             "l'est que par la prose, donc se redemande à chaque session."
                             % (" et mode `%s`" % h["mode"] if h["mode"] else ""))
    return "ok", "Conforme au starter."


def scanne(racine: pathlib.Path, un_seul=""):
    aujourdhui = datetime.date.today()
    out = []
    for d in sorted(racine.iterdir(), key=lambda x: x.name.lower()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        if not un_seul and d.name in IGNORE:
            continue
        if un_seul and d.name.lower() != un_seul.lower():
            continue
        h = harnais(d)
        _f, _etats = forme(d)
        # Une seule voix : l'état le plus en difficulté, et les tâches réunies.
        # À plusieurs agents, ce qui attend le commanditaire ne se range pas par agent.
        e, t = {}, []
        for _n, _m in _etats:
            _e = entete(lis(_m / "state.md"))
            if _e and (not e or _e.get("sante") == "rouge"):
                e = _e
            t += taches(lis(_m / "todo.md"))
        if _f != "ancienne":
            _b = entete(lis(d / ".fact" / "base.md"))
            e = dict(e)
            e.pop("cap", None)
            if _b.get("cap"):
                e["cap"] = _b["cap"]
        etat, jours = fraicheur(e.get("maj", ""), aujourdhui)
        code, conseil = verdict(h)
        out.append({
            "nom": d.name, "chemin": str(d), "harnais": h, "champs": e, "taches": t,
            "fraicheur": etat, "jours": jours, "verdict": code, "conseil": conseil,
            # Attend une décision : un destinataire nommé, quel qu'il soit.
            # `@dehors` est exclu — c'est une attente que personne ici ne lève.
            "attente": [x for x in t
                        if x["qui"] and x["qui"] != DEHORS and x["etat"] != "fait"],
            "encours": [x for x in t if x["etat"] == "encours"],
            "afaire": [x for x in t if x["etat"] == "afaire"],
        })
    return out


# ── sortie terminal ───────────────────────────────────────────────────────────

SYMBOLE = {"ok": "OK ", "neuf": "NEUF", "ancien": "TRI ", "incomplet": "MANQ",
           "sans-agent": "AGT?",
           "aveugle": "AVGL", "sans-briefing": "BRIEF", "sans-deny": "DENY",
           "sans-hooks": "HOOK", "non-cable": "CABL", "sans-git": "GIT ",
           "surplus": "6e  "}
FRAIS = {"frais": "à jour", "tiede": "tiède", "perime": "PÉRIMÉ", "illisible": "ILLISIBLE"}


def terminal(projets, racine):
    print("Atelier : %s — %d projet(s)\n" % (racine, len(projets)))
    attente_totale = []
    for p in projets:
        h, e = p["harnais"], p["champs"]
        print("── %-22s [%s] %s" % (p["nom"], SYMBOLE.get(p["verdict"], "?"), p["conseil"]))
        if e.get("cap"):
            print("     cap    : %s" % e["cap"][:90])
        maj = e.get("maj", "—")
        j = "" if p["jours"] is None else " (%d j)" % p["jours"]
        print("     maj    : %s — %s%s   santé : %s   jalon : %s"
              % (maj, FRAIS[p["fraicheur"]], j, e.get("sante", "—"), (e.get("jalon") or "—")[:44]))
        print("     harnais: git %s · hooks %d · câblés %s · %s · .logs %d"
              % ("oui" if h["git"] else "NON", len(h["hooks"]),
                 "oui" if h["cable"] else "NON", jauge(h), h["logs"]))
        print("     contexte: CLAUDE.md→mémoire %s · briefing %s · deny %s"
              % ("oui" if h["oriente"] else "NON",
                 "oui" if h["briefing"] else "NON",
                 len(h["deny"]) if h["deny"] is not None else "—"))
        if p["taches"]:
            print("     tâches : %d en cours · %d à faire · %d attendent une décision"
                  % (len(p["encours"]), len(p["afaire"]), len(p["attente"])))
        for a in p["attente"]:
            attente_totale.append((p["nom"], a))
        print()

    print("═" * 64)
    if attente_totale:
        print("CE QUI ATTEND UNE DÉCISION — %d point(s), la seule colonne qui ne se délègue pas\n"
              % len(attente_totale))
        for nom, a in sorted(attente_totale, key=lambda x: {"haut": 0, "moyen": 1, "": 2, "bas": 3}[x[1]["prio"]]):
            print("  [%-5s] %-18s @%-9s %s"
                  % (a["prio"] or "—", nom, a["qui"], a["titre"][:60]))
    else:
        print("Aucune tâche `@<qui>` ouverte — ce qui peut vouloir dire deux choses :")
        print("rien n'attend, ou personne n'en a déclaré. Le second cas est le plus fréquent.")


# ── sortie HTML autonome ──────────────────────────────────────────────────────

CSS = """
:root{--fond:#f3f4f6;--carte:#fff;--creux:#e9ebef;--encre:#15181e;--doux:#4a5160;
--pale:#767e8e;--trait:#d6d9e0;--accent:#3b4e8f;--vert:#2f7d4f;--orange:#9a6b12;
--rouge:#a5432f;--vert-f:#e4f0e9;--orange-f:#f7eeda;--rouge-f:#f6e7e3;--acc-f:#e6e9f4}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--fond:#14161b;
--carte:#1b1e25;--creux:#23272f;--encre:#e7e9ed;--doux:#a8afbd;--pale:#7c8494;
--trait:#2e333d;--accent:#9bb0e8;--vert:#7bc49a;--orange:#d8b45c;--rouge:#e2907e;
--vert-f:#1c2a22;--orange-f:#2c2618;--rouge-f:#33221e;--acc-f:#232b42}}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--encre);font:15px/1.6 -apple-system,
BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.p{max-width:78rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}
h1{font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.01em}
.sous{color:var(--pale);font-size:.9rem;margin:0 0 2rem}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,"Cascadia Mono",monospace}
.att{background:var(--carte);border:1px solid var(--trait);border-left:3px solid var(--rouge);
border-radius:5px;padding:1.1rem 1.25rem;margin-bottom:2rem}
.att h2{font-size:1rem;margin:0 0 .8rem;color:var(--rouge);letter-spacing:.02em}
.att ul{margin:0;padding-left:1.1rem}.att li{margin-bottom:.4rem}
.att .p-{display:inline-block;font-size:.68rem;padding:.08rem .4rem;border-radius:3px;
margin-right:.5rem;font-family:ui-monospace,monospace;background:var(--creux);color:var(--doux)}
.att .p-haut{background:var(--rouge-f);color:var(--rouge)}
.att .proj{color:var(--pale);font-size:.85rem}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(21rem,1fr));gap:.9rem}
.c{background:var(--carte);border:1px solid var(--trait);border-radius:6px;padding:1rem 1.1rem}
.c h3{margin:0;font-size:1.05rem;display:flex;align-items:center;gap:.5rem;flex-wrap:wrap}
.b{font-size:.66rem;padding:.12rem .45rem;border-radius:3px;font-family:ui-monospace,monospace;
letter-spacing:.03em;text-transform:uppercase}
.b-ok{background:var(--vert-f);color:var(--vert)}
.b-warn{background:var(--orange-f);color:var(--orange)}
.b-bad{background:var(--rouge-f);color:var(--rouge)}
.cap{color:var(--doux);font-size:.88rem;margin:.55rem 0 .8rem}
.meta{font-size:.79rem;color:var(--pale);font-family:ui-monospace,monospace;
border-top:1px solid var(--trait);padding-top:.6rem;margin-top:.2rem;
display:flex;flex-wrap:wrap;gap:.15rem .9rem}
.meta b{font-weight:500;color:var(--doux)}
.no{color:var(--rouge)}
.conseil{margin-top:.7rem;font-size:.83rem;background:var(--acc-f);color:var(--accent);
padding:.45rem .6rem;border-radius:4px}
.barre{display:flex;height:5px;border-radius:3px;overflow:hidden;background:var(--creux);margin:.7rem 0 .35rem}
.barre i{display:block}.b1{background:var(--vert)}.b2{background:var(--accent)}.b3{background:var(--trait)}
.tt{font-size:.78rem;color:var(--pale)}
footer{margin-top:2.5rem;padding-top:1rem;border-top:1px solid var(--trait);
color:var(--pale);font-size:.8rem}
"""

BADGE = {"ok": ("b-ok", "conforme"), "neuf": ("b-bad", "sans mémoire"),
         "sans-agent": ("b-bad", "aucun agent"),
         "ancien": ("b-bad", "taxonomie ancienne"), "incomplet": ("b-warn", "mémoire incomplète"),
         "sans-hooks": ("b-warn", "sans hooks"), "non-cable": ("b-warn", "non câblé"),
         "sans-git": ("b-warn", "sans git"), "surplus": ("b-warn", "6e fichier"),
         "aveugle": ("b-bad", "CLAUDE.md aveugle"),
         "sans-briefing": ("b-warn", "sans briefing"),
         "sans-deny": ("b-warn", "aucun deny")}
BADGE_FRAIS = {"frais": ("b-ok", "à jour"), "tiede": ("b-warn", "tiède"),
               "perime": ("b-bad", "périmé"), "illisible": ("b-bad", "en-tête illisible")}


def page(projets, racine, watch=0):
    e = html.escape
    att = [(p["nom"], a) for p in projets for a in p["attente"]]
    att.sort(key=lambda x: {"haut": 0, "moyen": 1, "": 2, "bas": 3}[x[1]["prio"]])

    bloc = ['<div class="att"><h2>Ce qui attend une décision — %d point(s)</h2>' % len(att)]
    if att:
        bloc.append("<ul>")
        for nom, a in att:
            bloc.append('<li><span class="p- p-%s">%s</span>%s '
                        '<span class="proj">— %s · @%s</span></li>'
                        % (e(a["prio"] or ""), e(a["prio"] or "—"), e(a["titre"]),
                           e(nom), e(a["qui"])))
        bloc.append("</ul>")
    else:
        bloc.append('<p style="margin:0;font-size:.9rem">Aucune tâche <span class="mono">@&lt;qui&gt;</span> '
                    'ouverte. Deux lectures possibles : rien n\'attend, ou personne n\'en a déclaré.</p>')
    bloc.append("</div>")

    cartes = []
    for p in projets:
        h, ch = p["harnais"], p["champs"]
        bv, bt = BADGE.get(p["verdict"], ("b-warn", p["verdict"]))
        fv, ft = BADGE_FRAIS[p["fraicheur"]]
        fait = len([x for x in p["taches"] if x["etat"] == "fait"])
        enc, af = len(p["encours"]), len(p["afaire"])
        tot = max(fait + enc + af, 1)
        c = ['<div class="c"><h3>%s <span class="b %s">%s</span> <span class="b %s">%s</span></h3>'
             % (e(p["nom"]), bv, e(bt), fv, e(ft))]
        c.append('<p class="cap">%s</p>' % e(ch.get("cap") or "— pas de <span>cap:</span> déclaré —"))
        if p["taches"]:
            c.append('<div class="barre"><i class="b1" style="width:%.1f%%"></i>'
                     '<i class="b2" style="width:%.1f%%"></i><i class="b3" style="width:%.1f%%"></i></div>'
                     % (100 * fait / tot, 100 * enc / tot, 100 * af / tot))
            c.append('<div class="tt">%d fait · %d en cours · %d à faire</div>' % (fait, enc, af))
        non = lambda ok, t: t if ok else '<span class="no">%s</span>' % t
        c.append('<div class="meta">'
                 '<span><b>maj</b> %s</span><span><b>santé</b> %s</span>'
                 '<span>%s</span><span>%s</span><span>%s</span><span><b>mémoire</b> %s</span>'
                 '<span><b>.logs</b> %d</span></div>'
                 % (e(ch.get("maj") or "—"), e(ch.get("sante") or "—"),
                    non(h["git"], "git"), non(bool(h["hooks"]), "hooks"),
                    non(h["cable"], "câblés"), e(jauge(h)), h["logs"]))
        c.append('<div class="meta"><span>%s</span><span>%s</span>'
                 '<span><b>deny</b> %s</span></div>'
                 % (non(h["oriente"], "CLAUDE.md → .mind"),
                    non(h["briefing"], "briefing"),
                    len(h["deny"]) if h["deny"] is not None else "—"))
        if p["verdict"] != "ok":
            c.append('<div class="conseil">%s</div>' % e(p["conseil"]))
        c.append("</div>")
        cartes.append("".join(c))

    # `meta refresh` est le SEUL rafraîchissement qui marche depuis `file://` :
    # un fetch y est interdit par la politique d'origine, et il n'y a pas de
    # serveur pour pousser quoi que ce soit. Le navigateur relit le fichier, et
    # `--watch` le réécrit à côté. Sans `--watch`, aucun refresh : une page qui
    # se recharge sans que rien ne la régénère ne ferait que clignoter.
    refresh = ("<meta http-equiv=refresh content=%d>" % watch) if watch else ""
    pied = ("Régénérée toutes les %d s tant que <span class=mono>--watch</span> "
            "tourne." % watch) if watch else \
           ("Relevé daté, pas un tableau vivant. Régénérer avec "
            "<span class=mono>agentic-team.py --html</span>.")

    return ("<!doctype html><html lang=fr><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>%s"
            "<title>Agentic Team</title><style>%s</style></head><body><div class=p>"
            "<h1>Agentic Team</h1>"
            "<p class=sous><span class=mono>%s</span> · %d projets · relevé du %s</p>"
            "%s<div class=g>%s</div>"
            "<footer>Page autonome : aucun serveur, aucune ressource externe. %s</footer>"
            "</div></body></html>"
            % (refresh, CSS, e(str(racine)), len(projets),
               datetime.datetime.now().strftime("%d/%m/%Y à %H:%M"),
               "".join(bloc), "".join(cartes), pied))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--racine", default=str(pathlib.Path.home() / "Agentic"))
    ap.add_argument("--projet", default="", help="n'examiner qu'un projet")
    ap.add_argument("--html", default="", help="écrire une page autonome à ce chemin")
    ap.add_argument("--watch", type=int, default=0, metavar="N",
                    help="avec --html : réécrire la page toutes les N secondes "
                         "et y poser un meta-refresh (60 s est un bon pas)")
    a = ap.parse_args()

    racine = pathlib.Path(a.racine).expanduser().resolve()
    if not racine.is_dir():
        raise SystemExit("Racine introuvable : %s" % racine)
    if a.watch and not a.html:
        raise SystemExit("--watch n'a de sens qu'avec --html : sans page à "
                         "réécrire, il n'y a rien à rafraîchir.")
    if a.watch and a.watch < 5:
        raise SystemExit("--watch en dessous de 5 s relit tous les .mind/ en "
                         "boucle pour rien. 60 s convient.")

    def releve():
        p = scanne(racine, a.projet)
        if not p:
            raise SystemExit("Aucun projet trouvé dans %s%s"
                             % (racine, " pour « %s »" % a.projet if a.projet else ""))
        return p

    if not a.html:
        terminal(releve(), racine)
        return

    cible = pathlib.Path(a.html).expanduser().resolve()
    cible.parent.mkdir(parents=True, exist_ok=True)

    def ecris():
        projets = releve()
        cible.write_text(page(projets, racine, a.watch), encoding="utf-8")
        return projets

    projets = ecris()
    print("Page écrite : %s  (%d projets, %.0f Ko)"
          % (cible, len(projets), cible.stat().st_size / 1024))
    if not a.watch:
        print("Elle s'ouvre d'un double-clic — aucun serveur nécessaire.")
        return

    print("Suivi toutes les %d s. La page se recharge seule ; Ctrl-C pour "
          "arrêter." % a.watch)
    # SIGTERM autant que Ctrl-C : mesuré, un `kill` simple laissait la balise
    # `refresh` en place et la page se rechargeait indéfiniment sur un relevé
    # mort. `sys.exit` depuis le gestionnaire lève SystemExit dans le thread
    # principal, donc le même nettoyage sert aux deux.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        while True:
            time.sleep(a.watch)
            ecris()
    except (KeyboardInterrupt, SystemExit):
        # Réécrire une dernière fois sans refresh : la page reste lisible et
        # cesse de se prétendre vivante. Si même ça échoue (disque plein, kill
        # -9), la date en tête reste le signal honnête — elle ne bouge plus.
        try:
            cible.write_text(page(releve(), racine, 0), encoding="utf-8")
            print("\nSuivi arrêté — la page reste en place, en relevé daté.")
        except Exception as exc:
            print("\nSuivi arrêté, mais la page garde son meta-refresh (%s). "
                  "Elle se rechargera sur un relevé figé : sa date en tête ne "
                  "bougera plus." % exc)


if __name__ == "__main__":
    main()
