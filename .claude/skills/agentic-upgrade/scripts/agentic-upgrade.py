#!/usr/bin/env python3
"""Onboarde un projet existant qui n'a PAS encore le harnais.

**Purement additif** : *copy-if-missing*. Ce script n'écrase jamais un fichier
du projet, et ne supprime rien — sauf `.claude/memory/` sur demande explicite
(`--remove-legacy-memory`), et seulement une fois `docs/` en place.

Ce qu'il fait est MÉCANIQUE : poser les fichiers manquants, signaler ce qu'il
n'a pas touché. Ce qui demande du JUGEMENT — trier le contenu d'une mémoire
ancienne, réconcilier `CLAUDE.md`, câbler les hooks dans un `settings.json`
déjà personnalisé — est piloté par le `SKILL.md`, pas par ce script. Un script
qui décide à la place de l'agent prend ses décisions sans avoir lu le projet.

**Dry-run par défaut.** `--apply` pour écrire.

Porté de PowerShell en Python le 03/09/2026, pour la même raison que
`agentic-sync` : le `.ps1` ne tournait que sur Windows, `pwsh` n'est pas
installé sur le Mac de l'atelier, et l'outil n'y avait donc jamais pu
s'exécuter. Python est déjà une dépendance dure du starter (les hooks en ont
besoin) : une seule implémentation couvre les deux plateformes.

Projet **déjà** au harnais, à remettre au niveau : c'est `agentic-sync`.
"""
import argparse, json, pathlib, shutil, subprocess, tempfile, uuid

DEPOT = "https://github.com/PetitPelican/claude-starter.git"

# Références obsolètes réécrites dans les fichiers de doc du projet.
# `.claude/memory/` était l'emplacement de la mémoire avant `docs/`.
REECRITURES = ((".claude/memory/", "docs/"), (".claude/memory", ".memory"))
CIBLES_REECRITURE = ("README.md", "CLAUDE.md", "docs/README.md")

# Restes d'un second harnais, retiré du starter le 03/09/2026. On les SIGNALE :
# les supprimer est le travail d'`agentic-sync`, pas d'un skill additif.
RESIDUS = (".codex", "AGENTS.md", ".claude/hooks/memory-guard.py",
           ".claude/skills/memory-update", ".claude/skills/caveman-compress",
           ".claude/skills/audit")

# Avant migration ; après, `.mind/` n'en tient que deux et `.fact/` les quatre.
MIND_ANCIEN = ("state.md", "todo.md", "stack.md", "architecture.md", "rules.md")
MIND_ATTENDU = ("state.md", "todo.md")
FACT_ATTENDU = ("base.md", "architecture.md", "stack.md", "rules.md")

# Taxonomie mémoire d'avant le 02/09/2026, telle qu'on la trouve sur le disque.
ANCIENS_NOMS = ("business.md", "clients.md", "charter.md")


class Rapport:
    def __init__(self):
        self.changements, self.ignores, self.manuel = [], [], []
    def change(self, m): self.changements.append(m)
    def ignore(self, m): self.ignores.append(m)
    def main_humaine(self, m): self.manuel.append(m)


def pose_reglages(src: pathlib.Path, dst: pathlib.Path, rap: Rapport,
                  appliquer: bool) -> bool:
    """Pose le `settings.json` du starter, mais **sans son `deny`**.

    Le starter interdit `git commit` et `git push` : c'est sa posture à lui, sur
    un dépôt neuf dont personne ne commite encore. La transposer telle quelle
    dans un projet EXISTANT casse deux choses d'un coup — l'agent ne peut plus
    committer alors qu'il le faisait la veille, et surtout `mind-guard` et
    `journal`, qui se déclenchent AU commit, deviennent inertes. Le harnais
    s'installerait en se désactivant lui-même, sans que rien ne le signale.

    On copie donc le CÂBLAGE des hooks — la seule partie qui fait travailler le
    harnais — et on laisse `deny` vide. Interdire git est une décision qui
    appartient au projet ; elle se prend après, en connaissance de cause."""
    if not src.is_file() or dst.exists():
        return False
    rap.change("Copier %s (hooks câblés, `deny` laissé VIDE)" % dst)
    if appliquer:
        reglages = json.loads(src.read_text(encoding="utf-8"))
        refuses = reglages.get("permissions", {}).get("deny") or []
        if refuses:
            reglages["permissions"]["deny"] = []
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(reglages, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    rap.main_humaine(
        "PERMISSIONS : le settings.json posé a un `deny` VIDE, exprès — le "
        "harnais ne coupe pas les commits d'un projet qui commitait. Mais un "
        "droit qui n'est écrit qu'en prose se redemande à chaque session : "
        "décider maintenant ce que ce projet interdit, et l'y écrire. "
        "Le starter, lui, refuse `git commit`, `git push` et leurs formes `rtk` "
        "— à reprendre seulement si ce projet ne doit pas committer seul.")
    return True


def copie_si_absent(src: pathlib.Path, dst: pathlib.Path, rap: Rapport,
                    appliquer: bool, silencieux: bool = False):
    """Le cœur du skill : on ajoute, on n'écrase pas.

    Un fichier déjà là est un fichier que le projet a peut-être personnalisé.
    On le laisse et on le dit — un écrasement silencieux est la seule façon de
    perdre du travail avec un outil censé être additif."""
    if not src.is_file():
        return False
    if dst.exists():
        if not silencieux:
            rap.ignore("Existe déjà, non écrasé : %s" % dst)
        return False
    rap.change("Copier %s" % dst)
    if appliquer:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return True


def copie_arbre_si_absent(src: pathlib.Path, dst: pathlib.Path, rap: Rapport,
                          appliquer: bool, silencieux: bool = False):
    """Fichier par fichier, jamais dossier par dossier.

    Un `.mind/` à moitié rempli doit se compléter, pas être ignoré en bloc
    parce que le dossier existe."""
    if not src.is_dir():
        return
    for f in sorted(p for p in src.rglob("*") if p.is_file()):
        copie_si_absent(f, dst / f.relative_to(src), rap, appliquer, silencieux)


def reecris(chemin: pathlib.Path, rap: Rapport, appliquer: bool):
    if not chemin.is_file():
        return
    try:
        avant = chemin.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    apres = avant
    for vieux, neuf in REECRITURES:
        apres = apres.replace(vieux, neuf)
    if apres != avant:
        rap.change("Réécrire les références obsolètes dans %s" % chemin)
        if appliquer:
            chemin.write_text(apres, encoding="utf-8")


def racine_template(donnee: str, rap: Rapport) -> pathlib.Path:
    """Le starter de référence : celui qu'on désigne, celui qui nous contient,
    ou un clone jetable."""
    def valide(p):
        return (p / ".claude").is_dir() and (p / "CLAUDE.md").is_file()
    if donnee:
        r = pathlib.Path(donnee).resolve()
        if not valide(r):
            raise SystemExit("TemplateRoot n'est pas un starter "
                             "(.claude/ + CLAUDE.md) : %s" % r)
        return r
    c = pathlib.Path(__file__).resolve().parent
    for _ in range(8):
        if valide(c) and (c / ".mind").is_dir():
            return c
        if c.parent == c:
            break
        c = c.parent
    tmp = pathlib.Path(tempfile.gettempdir()) / ("claude-starter-" + uuid.uuid4().hex)
    rap.change("Cloner le template vers %s" % tmp)
    subprocess.run(["git", "clone", "--depth", "1", DEPOT, str(tmp)],
                   check=True, capture_output=True)
    return tmp


def memoire(projet: pathlib.Path, template: pathlib.Path, rap: Rapport,
            appliquer: bool, retirer_ancienne: bool):
    """`.claude/memory/` (ancien emplacement) -> `docs/`, puis templates."""
    ancienne, mem = projet / ".claude" / "memory", projet / ".memory"

    if ancienne.is_dir() and mem.is_dir():
        rap.main_humaine("MÉMOIRE : .claude/memory/ ET docs/ existent tous "
                         "les deux. Fusion manuelle — ce script ne choisit pas "
                         "quelle version d'un fichier fait foi.")
    elif ancienne.is_dir():
        rap.change("Déplacer .claude/memory/ vers docs/ (%d fichier(s))"
                   % len([p for p in ancienne.rglob("*") if p.is_file()]))
        if appliquer:
            shutil.copytree(ancienne, mem)
        if retirer_ancienne:
            rap.change("Supprimer l'ancien .claude/memory/ (copie faite)")
            if appliquer:
                shutil.rmtree(ancienne)
        else:
            rap.ignore("Ancien .claude/memory/ conservé. --remove-legacy-memory "
                       "pour le supprimer après copie.")

    # Templates manquants, sans jamais écraser ce que la migration vient de poser.
    copie_arbre_si_absent(template / ".memory", mem, rap, appliquer, silencieux=True)
    copie_arbre_si_absent(template / ".mind", projet / ".mind", rap, appliquer,
                          silencieux=True)


def diagnostic_memoire(projet: pathlib.Path, rap: Rapport):
    """Lecture seule, sur les NOMS de fichiers.

    Ne migre rien : trier une mémoire demande de la LIRE, et son contenu
    appartient au projet. On remonte le choix à faire, pas la décision prise.

    Regarde les DEUX emplacements, l'ancien et le nouveau. En dry-run rien n'a
    encore bougé : ne lire que `docs/` rendrait le diagnostic muet
    exactement dans le mode où l'on décide s'il faut y aller."""
    mind = projet / ".mind"
    sources = [d for d in (projet / ".memory", projet / ".claude" / "memory")
               if d.is_dir()]
    def present(nom):
        return any((d / nom).is_file() for d in sources)

    trouves = [n for n in ANCIENS_NOMS if present(n)]
    if trouves:
        rap.main_humaine(
            "MÉMOIRE : taxonomie d'avant le 02/09/2026 — %s. La migration est un "
            "TRI, pas une création : business.md se scinde entre .fact/rules.md "
            "et .fact/architecture.md, clients.md et charter.md se dissolvent "
            "(rôle -> CLAUDE.md, objectif -> champ cap: de .mind/state.md), "
            "decisions.md RESTE dans docs/. Voir l'étape mémoire du SKILL."
            % ", ".join(trouves))
    montent = [n for n in ("state.md", "rules.md", "architecture.md")
               if present(n)]
    if montent:
        rap.main_humaine(
            "MÉMOIRE : %s sont dans docs/ alors que ce sont des FAITS "
            "ACTUELS : ils MONTENT dans .mind/. Le template vide vient d'être "
            "posé à côté — c'est le contenu qu'il faut y remonter, puis "
            "supprimer l'original." % ", ".join(montent))
    if mind.is_dir():
        migre = (projet / ".fact").is_dir()
        attendu = MIND_ATTENDU if migre else MIND_ANCIEN
        surplus = [p.name for p in sorted(mind.glob("*.md")) if p.name not in attendu]
        if surplus:
            rap.main_humaine(".mind/ porte %d fichier(s) de trop (%s) : .mind/ en "
                             "tient %s, le reste est à .fact/ ou docs/."
                             % (len(surplus), ", ".join(surplus),
                                "deux" if migre else "EXACTEMENT cinq"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--template-root", default="")
    ap.add_argument("--apply", action="store_true",
                    help="écrire réellement (sinon : dry-run)")
    ap.add_argument("--remove-legacy-memory", action="store_true",
                    help="supprimer .claude/memory/ une fois copié vers docs/")
    a = ap.parse_args()

    projet = pathlib.Path(a.project_root).resolve()
    if not projet.is_dir():
        raise SystemExit("ProjectRoot introuvable : %s" % projet)
    rap = Rapport()
    template = racine_template(a.template_root, rap)
    if template == projet:
        raise SystemExit("ProjectRoot et TemplateRoot sont le même dossier : %s" % projet)

    print("Agentic upgrade (additif)")
    print("ProjectRoot : %s" % projet)
    print("TemplateRoot: %s" % template)
    print("Mode        : %s" % ("APPLY" if a.apply else "DRY-RUN"))
    print()

    # 1. Mémoire : ancien emplacement, puis templates manquants.
    memoire(projet, template, rap, a.apply, a.remove_legacy_memory)

    # 2. Harnais. Les skills et les hooks se posent fichier par fichier ; un
    #    skill que le projet a modifié reste celui du projet.
    copie_arbre_si_absent(template / ".claude" / "skills",
                          projet / ".claude" / "skills", rap, a.apply)
    copie_arbre_si_absent(template / ".claude" / "hooks",
                          projet / ".claude" / "hooks", rap, a.apply)

    # 3. settings.json : le CÂBLAGE des hooks est project-owned. S'il existe
    #    déjà, un hook posé en 2. peut n'être branché nulle part — et un hook
    #    qui n'est pas câblé ne fait rien et ne le dit pas. (Un hook câblé qui
    #    ne DÉMARRE pas, lui, fait l'inverse : il bloque — voir agentic-init.)
    reglages = projet / ".claude" / "settings.json"
    if not pose_reglages(template / ".claude" / "settings.json", reglages,
                         rap, a.apply):
        rap.main_humaine("settings.json existe : vérifier que briefing "
                         "(SessionStart + UserPromptSubmit), mind-guard "
                         "(PreToolUse) et journal (PostToolUse) y sont câblés "
                         "comme dans celui du starter — deux déclarations "
                         "chacun, `python` ET `python3`.")

    # `.rtk/filters.toml` est project-owned (les filtres de CE dépôt) et inerte
    # sans le binaire RTK sur la machine : le poser ne dépend de rien.
    for rel in (".mcp.json.example", ".claude/settings.local.json.example",
                ".rtk/filters.toml", ".gitattributes"):
        copie_si_absent(template / rel, projet / rel, rap, a.apply)

    # 3b. CLAUDE.md. Absent, on pose le template — il porte le bloc de détection
    #     `[PROJECT_NAME]` qui envoie vers /project-init. Présent, il est au
    #     projet : on n'y touche pas, on le signale à réconcilier.
    if copie_si_absent(template / "CLAUDE.md", projet / "CLAUDE.md", rap,
                       a.apply, silencieux=True):
        rap.main_humaine("CLAUDE.md : template posé, encore en [PROJECT_NAME]. "
                         "Le remplir — /project-init le fait en le personnalisant.")
    else:
        rap.main_humaine("CLAUDE.md existe : réconcilier à la main le rôle, les "
                         "règles et la section Mémoire (deux dossiers, deux "
                         "natures ; les deux hooks). Il n'est jamais écrasé.")

    # 4. .gitignore : la ligne qui compte, sans toucher au reste.
    gi = projet / ".gitignore"
    ligne = ".claude/settings.local.json"
    if gi.is_file():
        texte = gi.read_text(encoding="utf-8", errors="replace")
        if ligne not in texte.splitlines():
            rap.change("Ajouter %s à .gitignore" % ligne)
            if a.apply:
                prefixe = "" if texte.endswith("\n") or not texte else "\n"
                gi.write_text(texte + prefixe + ligne + "\n", encoding="utf-8")
    else:
        copie_si_absent(template / ".gitignore", gi, rap, a.apply)

    # 5. Références obsolètes dans la doc du projet.
    for rel in CIBLES_REECRITURE:
        reecris(projet / rel, rap, a.apply)

    # 6. Restes d'un second harnais : signalés, jamais recréés ni supprimés ici.
    presents = [r for r in RESIDUS if (projet / r).exists()]
    if presents:
        rap.main_humaine("RESTES d'une version antérieure du starter : %s. "
                         "Retirés en amont le 03/09/2026 — ne pas les recréer. "
                         "C'est `/agentic-sync` qui les supprime, pas ce skill "
                         "qui n'enlève rien." % ", ".join(presents))

    # 7. Diagnostic mémoire (lecture seule).
    diagnostic_memoire(projet, rap)

    print("Changements :")
    print("\n".join("- %s" % c for c in rap.changements) or "- Aucun")
    print()
    print("Ignorés (non écrasés) :")
    print("\n".join("- %s" % m for m in rap.ignores) or "- Aucun")
    print()
    print("À reprendre à la main (voir le SKILL agentic-upgrade) :")
    print("\n".join("- %s" % m for m in rap.manuel) or "- Aucun")

    if not a.apply:
        print("\nDry-run seulement. Relancer avec --apply pour appliquer.")


if __name__ == "__main__":
    main()
