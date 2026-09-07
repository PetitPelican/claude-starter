#!/usr/bin/env python3
"""Resynchronise un projet DÉJÀ au harnais sur la dernière version du starter.

Partie MÉCANIQUE seulement (fichiers starter-owned) : miroir des skills et des
hooks, signalement du moteur de site, suppression de ce que le starter a retiré.
La partie JUGEMENT — réconcilier `CLAUDE.md`, migrer la mémoire, générer
`site.config.yml` — est pilotée par le `SKILL.md`, pas par ce script.

**Dry-run par défaut.** `--apply` pour écrire.

Porté de PowerShell en Python le 03/09/2026. Le `.ps1` ne tournait que sur
Windows : `pwsh` n'est pas installé sur le Mac de l'atelier, et cet outil n'y a
donc jamais pu s'exécuter. Python est déjà une dépendance dure du starter (les
hooks en ont besoin) : une seule implémentation couvre les deux plateformes,
plutôt qu'une par OS qu'il faudrait corriger deux fois.
"""
import argparse, filecmp, hashlib, os, pathlib, re, shutil, subprocess, sys, tempfile, uuid

# --- ownership manifest -------------------------------------------------------
# Moteur / assets de site (starter-owned) : NON écrasés par la passe mécanique.
# Écraser le moteur seul casse le build tant que site.config.yml n'est pas
# généré — on se contente de SIGNALER la divergence, la mise à jour se fait
# dans le bloc « site » guidé du SKILL.
MOTEUR_SITE = (
    "site/build_site.py", "site/publish.py", "site/requirements.txt",
    "site/.gitignore", "site/_assets/reference.docx",
)

# Chemins retirés ou renommés en amont : supprimés du projet s'ils existent.
A_SUPPRIMER = (
    # second harnais, retiré le 03/09/2026
    ".codex", "AGENTS.md",
    # renommés le 03/09/2026 : atelier-init -> agentic-init, equipe -> agentic-team.
    # Sans cette ligne, une resynchro AJOUTE les nouveaux et LAISSE les anciens :
    # deux skills aux mêmes déclencheurs, dont un figé pour toujours.
    ".claude/skills/atelier-init", ".claude/skills/equipe",
    # renommages plus anciens
    ".claude/agents", ".claude/skills/agent-init",
    ".claude/skills/doc-site", ".claude/skills/project-upgrade",
    # skills retirés le 03/09/2026 : leur travail est fait par les hooks
    ".claude/skills/memory-update", ".claude/skills/caveman-compress",
    ".claude/skills/audit",
    # hook remplacé par mind-guard
    ".claude/hooks/memory-guard.py",
)

# Fichiers project-owned rappelés à l'utilisateur : jamais touchés par ce script.
PROJET_POSSEDE = (
    "CLAUDE.md (rôle, règles) -> section Mémoire + règles à réconcilier à la main",
    ".mind/** et docs/** (contenu) -> migration de taxonomie via le SKILL, pas ce script",
    "site/site.config.yml, site/_content/** -> conservés ; générer la config si absente",
    "settings.json (permissions + CÂBLAGE des hooks) -> project-owned : vérifier que "
    "briefing (SessionStart + UserPromptSubmit), mind-guard (PreToolUse) et "
    "journal (PostToolUse) y sont câblés comme dans le settings.json du starter, "
    "chacun deux fois (python et python3). Vérifier aussi qu'il y a au moins une "
    "règle `deny` : un droit qui n'est écrit qu'en prose se redemande à chaque "
    "session (les scripts des hooks, eux, sont synchronisés)",
    ".env*, .mcp.json, settings.local.json -> conservés",
    ".rtk/filters.toml -> project-owned (les filtres RTK de CE dépôt) : conservé. "
    "S'il manque, le prendre dans le starter. Le binaire RTK, lui, s'installe sur "
    "la MACHINE (`brew install rtk` puis `rtk init -g`), pas dans le dépôt",
)

DEPOT = "https://github.com/<compte>/claude-starter.git"


def different(a: pathlib.Path, b: pathlib.Path) -> bool:
    """Deux fichiers diffèrent-ils *en contenu* ?

    Le CRLF de Windows et le LF du dépôt ne sont pas une divergence : sans
    cette normalisation, une machine Windows verrait tous les fichiers du
    starter comme modifiés, à chaque passage."""
    if not b.is_file():
        return True
    ba, bb = a.read_bytes(), b.read_bytes()
    if b"\0" in ba or b"\0" in bb:   # binaire (reference.docx) : comparaison brute
        return hashlib.sha256(ba).digest() != hashlib.sha256(bb).digest()
    def norme(x):
        return (x.decode("utf-8", "replace").lstrip("﻿")
                 .replace("\r\n", "\n").replace("\r", "\n"))
    return norme(ba) != norme(bb)


class Rapport:
    def __init__(self):
        self.changements, self.manuel = [], []
    def change(self, m): self.changements.append(m)
    def main_humaine(self, m): self.manuel.append(m)


def _a_miroiter(racine: pathlib.Path):
    """Les fichiers d'un côté du miroir, sans les artefacts locaux.

    MESURÉ le 06/09/2026 en resynchronisant <projet> Studio : le miroir parcourt
    le SYSTÈME DE FICHIERS, pas git. Le starter gitignore `__pycache__/`, donc
    ses `.pyc` n'y sont que des résidus d'exécution des hooks — et le sync les
    recopiait quand même dans le projet, du bytecode compilé pour la version de
    Python du poste source. Exclus des DEUX côtés : ni copiés, ni comptés
    absents, donc jamais supprimés chez le projet non plus."""
    for p in racine.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            yield p


def miroir(source: pathlib.Path, cible: pathlib.Path, rap: Rapport, appliquer: bool):
    """Miroir d'un dossier 100 % starter-owned.

    Ajoute et écrase depuis le template, puis supprime dans le projet ce qui
    n'existe plus en amont — mais **uniquement ce qui existait avant la copie**,
    pour ne jamais supprimer un fichier fraîchement écrit."""
    if not source.is_dir():
        return
    avant = set()
    if cible.is_dir():
        avant = {p.relative_to(cible).as_posix() for p in _a_miroiter(cible)}
    en_source = set()
    for f in sorted(_a_miroiter(source)):
        rel = f.relative_to(source).as_posix()
        en_source.add(rel)
        dest = cible / rel
        if different(f, dest):
            rap.change("Sync %s" % dest)
            if appliquer:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
    for rel in sorted(avant - en_source):
        rap.change("Supprimer obsolète %s" % (cible / rel))
        if appliquer:
            (cible / rel).unlink()


def racine_template(donnee: str, rap: Rapport) -> pathlib.Path:
    """Le starter de référence : celui qu'on désigne, celui qui nous contient,
    ou un clone jetable."""
    def valide(p): return (p / ".claude").is_dir() and (p / "CLAUDE.md").is_file()
    if donnee:
        r = pathlib.Path(donnee).resolve()
        if not valide(r):
            raise SystemExit("TemplateRoot n'est pas un starter (.claude/ + CLAUDE.md) : %s" % r)
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


def detecte_ancienne_memoire(projet: pathlib.Path, rap: Rapport):
    """Lecture seule, sur les NOMS de fichiers uniquement.

    Ne migre rien : la migration est un tri qui demande de lire le contenu, et
    le contenu appartient au projet. On remonte le CHOIX, pas la décision."""
    mem, mind = projet / ".memory", projet / ".mind"
    montent = [n for n in ("state.md", "rules.md", "architecture.md")
               if (mem / n).is_file()]
    if montent and not mind.is_dir():
        rap.main_humaine(
            "MÉMOIRE : taxonomie d'avant le 02/09/2026 — %s sont encore dans "
            "docs/ et .mind/ n'existe pas. La migration est un TRI, pas une "
            "création : ces fichiers MONTENT dans .mind/, decisions.md RESTE, "
            "charter.md se dissout (rôle -> CLAUDE.md, objectif -> champ cap:). "
            "Voir l'étape mémoire du SKILL. Rien migré d'office."
            % ", ".join(montent))
    elif (mem / "charter.md").is_file():
        rap.main_humaine(
            "MÉMOIRE : docs/charter.md subsiste. Il a été retiré du template le "
            "03/09/2026 — son contenu se répartit entre le champ cap: de "
            ".fact/base.md, les frontières de .fact/architecture.md, .fact/stack.md "
            "et CLAUDE.md. À dissoudre à la main.")
    # Trois formes coexistent depuis le 04/09/2026 : avant migration les cinq
    # fichiers sont dans `.mind/` ; après, quatre dans `.fact/` et deux dans
    # `.mind/`, ce dernier pouvant être répété sous `agents/<nom>/`.
    migre = (projet / ".fact").is_dir()
    if mind.is_dir():
        fichiers = sorted(p.name for p in mind.glob("*.md"))
        attendus = ({"state.md", "todo.md"} if migre else
                    {"state.md", "todo.md", "stack.md", "architecture.md", "rules.md"})
        surplus = [f for f in fichiers if f not in attendus]
        manque = sorted(attendus - set(fichiers))
        combien = "deux (state, todo)" if migre else "EXACTEMENT cinq"
        if surplus:
            rap.main_humaine(".mind/ porte %d fichier(s) de trop (%s) : .mind/ en tient "
                             "%s, le reste appartient à .fact/ ou docs/."
                             % (len(surplus), ", ".join(surplus), combien))
        if manque:
            rap.main_humaine(".mind/ est incomplet : %s manque(nt)." % ", ".join(manque))
    if migre:
        attendus = {"base.md", "architecture.md", "stack.md", "rules.md"}
        vus = {x.name for x in (projet / ".fact").glob("*.md")}
        if vus - attendus:
            rap.main_humaine(".fact/ porte %d fichier(s) de trop (%s) : il est FERMÉ à "
                             "quatre — base, architecture, stack, rules."
                             % (len(vus - attendus), ", ".join(sorted(vus - attendus))))
        if attendus - vus:
            rap.main_humaine(".fact/ est incomplet : %s manque(nt)."
                             % ", ".join(sorted(attendus - vus)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--template-root", default="")
    ap.add_argument("--apply", action="store_true",
                    help="écrire réellement (sinon : dry-run)")
    a = ap.parse_args()

    projet = pathlib.Path(a.project_root).resolve()
    if not projet.is_dir():
        raise SystemExit("ProjectRoot introuvable : %s" % projet)
    rap = Rapport()
    template = racine_template(a.template_root, rap)

    print("Agentic sync")
    print("ProjectRoot : %s" % projet)
    print("TemplateRoot: %s" % template)
    print("Mode        : %s" % ("APPLY" if a.apply else "DRY-RUN"))
    print()

    # 1. Miroir des skills, skill par skill : préserve les skills propres au projet.
    tpl_skills = template / ".claude" / "skills"
    if tpl_skills.is_dir():
        for skill in sorted(p for p in tpl_skills.iterdir() if p.is_dir()):
            miroir(skill, projet / ".claude" / "skills" / skill.name, rap, a.apply)

    # 1b. Miroir des hooks. Le CÂBLAGE (settings.json) reste project-owned.
    miroir(template / ".claude" / "hooks", projet / ".claude" / "hooks", rap, a.apply)

    # 2. Moteur de site : signalé, jamais écrasé ici.
    for rel in MOTEUR_SITE:
        src, dst = template / rel, projet / rel
        if src.is_file() and dst.is_file() and different(src, dst):
            rap.main_humaine("site : %s diffère du template -> migration guidée "
                             "(bloc site du SKILL), NON écrasé automatiquement" % rel)

    # 3. Suppression de ce que le starter a retiré ou renommé.
    # Un fichier « retiré en amont » peut être devenu le SEUL contexte d'un
    # projet. Mesuré le 03/09/2026 : un dépôt dont le `CLAUDE.md` tenait en une
    # ligne, `@AGENTS.md`, aurait perdu ses 89 lignes de contexte et gardé un
    # import vers un fichier effacé — sans erreur, l'agent démarrant simplement
    # sans rien savoir de son projet. On ne supprime jamais une cible d'import.
    def _texte(f):
        try:
            return f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    importes = set()
    for f in (projet / "CLAUDE.md", projet / "AGENTS.md"):
        for imp in re.findall(r"^@(\S+)", _texte(f), re.M):
            importes.add(imp.lstrip("./"))

    for rel in A_SUPPRIMER:
        p = projet / rel
        if not p.exists():
            continue
        if rel in importes:
            rap.main_humaine(
                "NE PAS supprimer %s : le `CLAUDE.md` de ce projet l'IMPORTE "
                "(`@%s`). Le retirer laisserait un import vers un fichier "
                "absent, donc un agent sans contexte, sans la moindre erreur. "
                "Reverser son contenu dans `CLAUDE.md` et `.mind/` d'abord, "
                "puis le supprimer à la main." % (rel, rel))
            continue
        rap.change("Supprimer %s (retiré en amont)" % rel)
        if a.apply:
            shutil.rmtree(p) if p.is_dir() else p.unlink()

    # 4. Détection (lecture seule) d'une taxonomie mémoire ancienne.
    detecte_ancienne_memoire(projet, rap)

    # 5. Rappels : zones à réconcilier à la main.
    for m in PROJET_POSSEDE:
        rap.main_humaine(m)

    print("Changements (mécaniques) :")
    print("\n".join("- %s" % c for c in rap.changements) or "- Aucun")
    print()
    print("À réconcilier à la main (project-owned — voir le SKILL agentic-sync) :")
    print("\n".join("- %s" % m for m in rap.manuel) or "- Aucun")

    if not a.apply:
        print("\nDry-run seulement. Relancer avec --apply pour appliquer la partie mécanique.")


if __name__ == "__main__":
    main()
