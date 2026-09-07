#!/usr/bin/env python3
"""Fait le ménage d'un projet — ou de tout un atelier — sans jamais décider à la
place de quelqu'un.

Trois familles, rendues SÉPARÉMENT parce qu'elles n'ont pas la même nature :

  1. CACHES RÉGÉNÉRABLES  supprimés (sous `--apply`), avec la commande qui les
                          refait. Un `node_modules` n'est pas une donnée.
  2. RÉSIDUS DE MIGRATION listés seulement. Ce sont des phrases que quelqu'un a
                          écrites ; seul l'agent du projet sait si elles sont
                          reprises ailleurs.
  3. MÉMOIRE HYPERTROPHIÉE listée seulement. Trier, c'est choisir ce qu'on
                          oublie — un programme n'a pas à le faire.

**Dry-run par défaut.** `--apply` n'agit QUE sur la famille 1.

Pourquoi ce skill existe. Les agents ne font pas le ménage, et le reproche est
mal placé : aucun outil ne le faisait. `agentic-sync` ne retire que ce que le
starter a retiré, `agentic-upgrade` est purement additif. Personne n'était
chargé du reste — mesuré le 03/09/2026 sur l'atelier de référence, 10,4 Go de
cache jamais nettoyé sur un disque à 92 %.
"""
import argparse, os, pathlib, re, shutil, stat, subprocess, sys

# --- famille 1 : ce qui se refait tout seul -----------------------------------
# Chaque entrée dit COMMENT ça repousse. Sans cette colonne, la suppression est
# un pari ; avec elle, c'est une opération réversible et on peut le vérifier.
CACHES = {
    "node_modules":   "npm ci  (ou pnpm install / yarn install)",
    ".turbo":         "refait seul au prochain `turbo`",
    ".next":          "npm run build",
    ".astro":         "npm run build  (ou `astro sync`)",
    ".nuxt":          "npm run build",
    ".svelte-kit":    "npm run build",
    ".parcel-cache":  "refait seul au prochain build",
    ".vite":          "refait seul au prochain build",
    # `dist` et `build` n'appartiennent à aucun écosystème : voir `refait_par()`.
    "dist":           "",
    "build":          "",
    ".venv":          "uv sync  (ou python3 -m venv .venv && pip install -r requirements.txt)",
    "venv":           "uv sync  (ou python3 -m venv venv && pip install -r requirements.txt)",
    "__pycache__":    "refait seul à l'import suivant",
    ".mypy_cache":    "refait seul au prochain mypy",
    ".pytest_cache":  "refait seul au prochain pytest",
    ".ruff_cache":    "refait seul au prochain ruff",
    ".gradle":        "refait seul au prochain build Gradle",
    "DerivedData":    "refait seul au prochain build Xcode",
    # Swift Package Manager. Absent de la première version de cette liste, et
    # c'est un agent de projet qui l'a trouvé en mesurant à la main : 192 Mo
    # invisibles dans `ios/<Module>Core/.build`. Une liste de noms de
    # caches ne se devine pas, elle se corrige sur le terrain.
    ".build":         "refait seul au prochain `swift build`",
    "Pods":           "pod install",
    "coverage":       "refait seul au prochain run de tests",
    ".nyc_output":    "refait seul au prochain run de tests",
}

# On ne descend jamais DANS un cache : y chercher d'autres caches coûte des
# minutes sur un `node_modules` de 6 Go pour ne rien apprendre.
NE_PAS_DESCENDRE = set(CACHES) | {".git"}

# --- famille 2 : ce que les migrations ont laissé derrière --------------------
# Les deux listes ci-dessous sont REPRISES telles quelles des outils qui les
# portaient déjà — `ANCIENS` d'`agentic-team.py`, `MONTENT` de la détection
# d'`agentic-sync.py`. Ne pas en inventer une troisième : trois listes de noms
# de fichiers finissent par diverger, et c'est le projet qui se fait reprocher
# une incohérence entre deux outils.
#
# Elles ne disent pas la même chose, d'où deux messages distincts : `MONTENT`
# nomme des fichiers qui ont une place ailleurs, `ANCIENS` des fichiers qui
# n'en ont plus. Et tout ce qui n'est dans ni l'une ni l'autre — `finances.md`,
# `concurrence.md`, `data-model.md` — est de la MATIÈRE DE DOMAINE, parfaitement
# à sa place dans `docs/`, qu'on se garde bien de signaler.
MONTENT = ("state.md", "rules.md", "architecture.md")
ANCIENS = ("charter.md", "business.md", "clients.md", "overview.md")
ANCIENNE_TAXONOMIE = set(MONTENT) | set(ANCIENS)
RESIDUS = re.compile(r"\.(bak|old|orig|sav)\b|\.bak[-.]|\.avant[-.]|~$", re.I)

# `docs/` ne contient que de l'écrit à la main (règle du 04/09/2026). Une sortie
# de build qui y tombe brouille la seule ligne qui compte ici : ce qui se
# régénère et ce qui ne se régénère pas.
GENERE = (".pdf", ".html", ".png", ".jpg", ".jpeg", ".zip", ".docx", ".xlsx", ".svg")


def dossier_memoire(projet):
    """`docs/` après migration, `.memory/` avant. La FORME décide, jamais la
    simple présence d'un `docs/` : des projets non migrés en ont déjà un,
    rempli de sorties de build."""
    return (projet / "docs") if (projet / ".fact").is_dir() else (projet / ".memory")

# --- famille 3 ----------------------------------------------------------------
SEUIL_LIGNES = 500
DATE = re.compile(r"\b(20\d\d)[-/](\d\d)[-/](\d\d)\b|\b(\d\d)/(\d\d)/(20\d\d)\b")


class Rapport:
    def __init__(self):
        self.caches, self.residus, self.memoire, self.manuel = [], [], [], []


def mo(n: int) -> float:
    return n / 1048576.0


def poids(chemin: pathlib.Path, vus: set | None = None) -> int:
    """Taille d'une arborescence, en octets — comptée comme `du` la compte.

    Deux pièges, tous deux mesurés le 03/09/2026 sur un monorepo pnpm :

    · Les LIENS DURS. pnpm ne copie pas ses paquets, il les relie : le même
      inode apparaît dans dix `node_modules`. Compter chaque lien annonçait
      13 950 Mo récupérables sur un projet qui en pèse 9 488 — un outil qui
      surestime le gain fait prendre une décision sur un chiffre faux. On ne
      compte donc chaque `(device, inode)` qu'une fois.
    · Les SYMLINKS, jamais suivis : un lien vers un volume externe compterait
      le volume."""
    if vus is None:
        vus = set()
    total = 0
    for racine, _, fichiers in os.walk(chemin, followlinks=False):
        for f in fichiers:
            p = os.path.join(racine, f)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            if stat.S_ISLNK(st.st_mode):
                continue
            cle = (st.st_dev, st.st_ino)
            if st.st_nlink > 1:
                if cle in vus:
                    continue
                vus.add(cle)
            total += st.st_size
    return total


def ignore_par_git(projet: pathlib.Path, chemin: pathlib.Path) -> bool | None:
    """`True` ignoré, `False` suivi, `None` pas un dépôt git.

    C'est le discriminant de tout le skill. Un cache ignoré par git est du
    déchet ; le MÊME dossier suivi par git est du contenu que quelqu'un a
    décidé de versionner, et le supprimer serait une perte, pas un ménage."""
    if not (projet / ".git").exists():
        return None
    try:
        r = subprocess.run(["git", "-C", str(projet), "check-ignore", "-q",
                            str(chemin)], capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.returncode == 0


def refait_par(cache: pathlib.Path) -> str:
    """Comment CE dossier-là se reconstruit.

    `dist/` et `build/` ne disent rien de leur écosystème : le même nom couvre
    du npm, du PyInstaller et du setuptools. Annoncer « npm run build » devant
    un `packaging/dist` produit par PyInstaller, c'est mettre une fausse
    garantie en face d'une suppression — relevé le 03/09/2026 sur un projet
    Python dont le rapport promettait une commande npm qui n'existe pas.

    On regarde donc ce qui se trouve À CÔTÉ, puis chez le parent."""
    fixe = CACHES.get(cache.name, "")
    if fixe:
        return fixe
    for dossier in (cache.parent, cache.parent.parent):
        if not dossier.is_dir():
            continue
        if list(dossier.glob("*.spec")):
            return "pyinstaller <le .spec d'à côté>"
        if (dossier / "package.json").is_file():
            return "npm run build"
        if (dossier / "pyproject.toml").is_file():
            return "python -m build  (ou le script de packaging du projet)"
        if (dossier / "Cargo.toml").is_file():
            return "cargo build"
    return "LE BUILD DU PROJET — non identifié, vérifier avant de supprimer"


def cherche_caches(projet: pathlib.Path):
    """Les caches, sans jamais descendre dans un cache déjà trouvé."""
    trouves = []
    for racine, dossiers, _ in os.walk(projet, topdown=True):
        garde = []
        for d in dossiers:
            if d in CACHES:
                trouves.append(pathlib.Path(racine) / d)
            elif d not in NE_PAS_DESCENDRE:
                garde.append(d)
        dossiers[:] = garde
    return sorted(trouves)


def famille_caches(projet: pathlib.Path, rap: Rapport, appliquer: bool) -> int:
    """Supprime — c'est la SEULE famille qui écrit.

    Le set `vus` est partagé par TOUS les caches du projet : sans cela, deux
    `node_modules` pnpm qui pointent le même inode seraient comptés deux fois,
    chacun de son côté."""
    rendu, vus, menus = 0, set(), []
    for c in cherche_caches(projet):
        p = poids(c, vus)
        rel = c.relative_to(projet).as_posix()
        etat = ignore_par_git(projet, c)
        if etat is False:
            rap.residus.append(
                "%-42s %8.1f Mo  SUIVI PAR GIT — pas supprimé. C'est un "
                "problème de .gitignore, pas de ménage." % (rel, mo(p)))
            continue
        if etat is None and c.name in ("dist", "build", "coverage"):
            rap.residus.append(
                "%-42s %8.1f Mo  hors dépôt git et nom ambigu — pas supprimé, "
                "vérifier que ce n'est pas de la source." % (rel, mo(p)))
            continue
        # Un monorepo a vingt `.turbo` vides. Les lister tous noie les trois
        # lignes qui portent 8 Go — et un rapport qu'on ne lit pas ne protège
        # de rien. On les compte, on ne les détaille pas.
        if mo(p) < 1.0:
            menus.append(rel)
        else:
            rap.caches.append("%-42s %8.1f Mo  <- %s"
                              % (rel, mo(p), refait_par(c)))
        rendu += p
        if appliquer:
            shutil.rmtree(c, ignore_errors=True)
    if menus:
        rap.caches.append("%-42s %8s     %d dossier(s) : %s"
                          % ("(caches de moins de 1 Mo)", "<1 Mo", len(menus),
                             ", ".join(sorted({pathlib.Path(m).name for m in menus}))))
    return rendu


def famille_residus(projet: pathlib.Path, rap: Rapport):
    """Listée, jamais supprimée."""
    memoire = dossier_memoire(projet)
    if memoire.name == "docs" and memoire.is_dir():
        genere = sorted(f.name for f in memoire.rglob("*") if f.suffix.lower() in GENERE)
        if genere:
            rap.residus.append(
                "docs/ porte %d fichier(s) qui ressemblent à des sorties de build "
                "(%s) : `docs/` ne contient que de l'écrit à la main — les sortir "
                "vers `site/` ou un dossier de build."
                % (len(genere), ", ".join(genere[:5]) + (", …" if len(genere) > 5 else "")))
    if memoire.is_dir():
        for f in sorted(memoire.glob("*.md")):
            if f.name in MONTENT:
                rap.residus.append(
                    "%s/%-33s dit des FAITS ACTUELS : MONTE dans .fact/ ou "
                    ".mind/, il y a déjà sa place" % (memoire.name, f.name))
            elif f.name in ANCIENS:
                rap.residus.append(
                    "%s/%-33s taxonomie d'avant le 02/09/2026 : à trier, son "
                    "contenu se répartit entre .fact/, .mind/ et docs/"
                    % (memoire.name, f.name))
        archive = memoire / "archive"
        if archive.is_dir():
            fs = [p for p in archive.rglob("*") if p.is_file()]
            couverts = [p for p in fs if p.name in ANCIENNE_TAXONOMIE]
            rap.residus.append(
                "docs/archive/%-25s %d fichier(s), %.1f Mo — dont %d repris "
                "par .mind/ (%s)" % ("", len(fs), mo(poids(archive)),
                                     len(couverts),
                                     ", ".join(sorted({p.name for p in couverts}))
                                     or "aucun"))
    for racine, dossiers, fichiers in os.walk(projet, topdown=True):
        dossiers[:] = [d for d in dossiers if d not in NE_PAS_DESCENDRE]
        for f in fichiers:
            if RESIDUS.search(f):
                p = pathlib.Path(racine) / f
                rap.residus.append(
                    "%-42s %8.1f Mo  sauvegarde manuelle"
                    % (p.relative_to(projet).as_posix(), mo(p.stat().st_size)))


def famille_memoire(projet: pathlib.Path, rap: Rapport):
    """Listée, jamais touchée. Trier, c'est choisir ce qu'on oublie."""
    memoire = dossier_memoire(projet)
    if not memoire.is_dir():
        return
    for f in sorted(memoire.rglob("*.md")):
        try:
            lignes = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        if len(lignes) < SEUIL_LIGNES:
            continue
        dates = sorted(m.group(0) for l in lignes for m in [DATE.search(l)] if m)
        rap.memoire.append(
            "%-42s %5d lignes  la plus ancienne entrée datée : %s"
            % (f.relative_to(projet).as_posix(), len(lignes),
               dates[0] if dates else "aucune date lisible"))


def nettoie(projet: pathlib.Path, rap: Rapport, appliquer: bool) -> int:
    rendu = famille_caches(projet, rap, appliquer)
    famille_residus(projet, rap)
    famille_memoire(projet, rap)
    return rendu


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projet", default=".", help="le projet à nettoyer (défaut : .)")
    ap.add_argument("--racine", default="",
                    help="au lieu d'un projet : tous les sous-dossiers de ce dossier")
    ap.add_argument("--apply", action="store_true",
                    help="supprimer réellement les caches (famille 1 seulement)")
    a = ap.parse_args()

    if a.racine:
        racine = pathlib.Path(os.path.expanduser(a.racine)).resolve()
        cibles = sorted(p for p in racine.iterdir()
                        if p.is_dir() and not p.name.startswith("."))
    else:
        cibles = [pathlib.Path(os.path.expanduser(a.projet)).resolve()]

    print("Agentic clean — %s" % ("APPLY" if a.apply else "DRY-RUN"))
    print("Cible%s : %s" % ("s" if len(cibles) > 1 else "",
                            ", ".join(c.name for c in cibles)))
    print()

    total = 0
    for cible in cibles:
        if not cible.is_dir():
            continue
        rap = Rapport()
        rendu = nettoie(cible, rap, a.apply)
        total += rendu
        if not (rap.caches or rap.residus or rap.memoire):
            continue
        print("═" * 78)
        print("  %s" % cible.name)
        print("═" * 78)
        if rap.caches:
            print("\n1. CACHES RÉGÉNÉRABLES — %s (%.1f Mo)"
                  % ("SUPPRIMÉS" if a.apply else "à supprimer", mo(rendu)))
            for m in rap.caches:
                print("   " + m)
        if rap.residus:
            print("\n2. RÉSIDUS — listés seulement, à trancher par l'agent du projet")
            for m in rap.residus:
                print("   " + m)
        if rap.memoire:
            print("\n3. MÉMOIRE AU-DELÀ DE %d LIGNES — à découper, jamais "
                  "automatiquement" % SEUIL_LIGNES)
            for m in rap.memoire:
                print("   " + m)
        print()

    print("─" * 78)
    print("Total récupérable : %.1f Mo" % mo(total))
    if not a.apply:
        print("\nDry-run. `--apply` supprime la FAMILLE 1 seulement — les "
              "familles 2 et 3 ne sont jamais supprimées par ce script.")
    else:
        print("\nLes familles 2 et 3 n'ont pas été touchées : elles demandent "
              "un jugement sur du contenu, pas une règle.")


if __name__ == "__main__":
    main()
