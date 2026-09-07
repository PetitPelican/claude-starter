#!/usr/bin/env python3
"""agentic-agents — convertit un projet MONO en MULTI, ou lui ajoute un agent.

UN SEUL SKILL, DEUX COMPORTEMENTS, ET C'EST LA FORME DU PROJET QUI DÉCIDE.
Sur un projet mono il convertit et crée les premiers agents ; sur un projet
déjà multi il en ajoute un. Les deux opérations sont la même à une étape près,
et deux entrées auraient divergé.

CE QU'IL FAIT
    .mind/{state,todo}.md        ->  agents/<premier>/.mind/
    .claude/settings.json        ->  agents/<premier>/.claude/, hooks en ../../
    ~/.claude/projects/<slug>/   ->  copié vers le slug du dossier d'agent
    agents/<autres>/             ->  créés vides (CLAUDE.md, settings, .mind)

CE QU'IL NE FAIT PAS
    - Il ne découpe pas le `CLAUDE.md`. C'est éditorial : le commun reste en
      haut, le rôle descend, et seul un humain sait où passe la ligne. Le
      script pose le fichier de rôle et dit quoi y mettre.
    - Il ne supprime pas l'ancienne mémoire auto : il la marque `.migre-<date>`.
      Précédent du 04/09/2026, renommage TrimTennis -> <projet> Studio.
    - Il ne touche pas à `.fact/`, `docs/`, `.logs/` ni au code : rien de tout
      ça n'appartient à un agent.

LE PIÈGE QU'IL EXISTE POUR ÉVITER. La mémoire auto d'un agent est classée par
CHEMIN (`~/.claude/projects/<chemin-slugifié>/`). Convertir déplace le `cwd` de
l'agent de `<projet>/` vers `<projet>/agents/<nom>/` : sans migration, l'agent
repart sur une adresse neuve et vide, et `--resume` ne retrouve plus rien. Au
04/09/2026 ça représentait 428 Mo et 20 fils pour <projet>, 58 Mo et 31 mémoires
pour <cto>.

**Dry-run par défaut.** `--apply` pour écrire.
"""
import argparse, datetime, json, pathlib, re, shutil, subprocess, sys

HOME = pathlib.Path.home()
ROLE = """# %s — rôle

> Le `CLAUDE.md` du projet est **hérité** : il est chargé en même temps que
> celui-ci, à chaque démarrage. N'y recopier AUCUNE de ses phrases. Le test :
> si une phrase resterait vraie pour un autre agent du projet, elle est à
> l'étage au-dessus.

## Ce que cet agent tient

[LE_PÉRIMÈTRE — en dossiers, pas en intentions. « orienté produit » n'empêche
personne de toucher au backend ; la frontière qui tient est celle écrite en
`deny` dans `.claude/settings.json`, à côté.]

## Ce qu'il ne touche pas

[LES_AUTRES_LOTS — et qui les tient.]
"""


def slug(p):
    """Mesuré le 04/09/2026 contre `~/.claude/projects/` : tout ce qui n'est
    pas alphanumérique devient un tiret. Vérifié sur six dossiers réels, dont
    un à espace (`<projet> Studio`)."""
    return re.sub(r"[^A-Za-z0-9]+", "-", str(p))


def git(p, *a):
    try:
        return subprocess.run(("git", "-C", str(p)) + a, capture_output=True,
                              text=True, timeout=15).returncode == 0
    except Exception:
        return False


def forme(p):
    agents = p / "agents"
    etats = []
    if agents.is_dir():
        etats = [d.name for d in sorted(agents.iterdir()) if (d / ".mind").is_dir()]
    if etats:
        return "multi", etats
    return ("mono" if (p / ".fact").is_dir() else "ancienne"), []


def reglages_agent(sources, cible, projet, autres, appliquer, rap):
    """Les hooks n'ont qu'un exemplaire, à la racine ; l'agent les appelle en
    `../../`. Et le périmètre s'écrit en `deny` ANCRÉ SUR LE HOME : mesuré le
    04/09/2026, un motif relatif (`Edit(../autre/**)`) ne mord pas.

    `sources` est une LISTE de candidats, dans l'ordre de préférence : la
    première qui existe gagne. Avant le 04/09/2026 c'était un chemin unique, et
    les agents NEUFS pointaient sur un `settings.agent.json.example` que presque
    aucun projet ne porte — ils naissaient donc sans hook, sans `defaultMode`, et
    le rapport annonçait quand même « hooks en ../../ ». Relevé sur la
    conversion réelle de <projet> : `<projet> PO` est né avec 7 lignes de JSON."""
    src = next((s for s in sources if s and s.is_file()), None)
    d = json.loads(src.read_text(encoding="utf-8")) if src else {}
    for blocs in d.get("hooks", {}).values():
        for bloc in blocs:
            for h in bloc.get("hooks", []):
                # Ancré sur CLAUDE_PROJECT_DIR, pas relatif au cwd. Mesuré le
                # 04/09/2026 : le hook tourne avec le cwd du dossier de lancement
                # de l'agent, donc un `../../` nu marche aujourd'hui — mais il
                # dépend d'un cwd qu'on ne contrôle pas, et un hook qui ne part
                # pas ne bloque rien et ne le dit pas. Le repli `:-.` garde la
                # forme relative si la variable manque, plutôt qu'un `/.claude/`
                # absolu qui échouerait en silence.
                m = re.match(r"^(python3?) \.claude/hooks/(\S+)$", h.get("command", ""))
                if m:
                    h["command"] = (
                        '%s "${CLAUDE_PROJECT_DIR:-.}/../../.claude/hooks/%s"' % (m.group(1), m.group(2))
                    )
    perm = d.setdefault("permissions", {})
    deny = [x for x in perm.get("deny", []) if "/agents/" not in x]
    # Ancré sur le home QUAND le projet y est. Un `~/` collé devant un chemin
    # absolu donnerait `~//private/tmp/...`, qui ne matche rien — et un deny
    # qui ne matche rien ne dit pas qu'il ne matche rien.
    try:
        maison = "~/" + str(projet.relative_to(HOME))
    except ValueError:
        maison = str(projet)
    deny += ["Edit(%s/agents/%s/**)" % (maison, a) for a in autres]
    perm["deny"] = deny
    # Dire ce qui s'est passé, pas ce qui était prévu. Un agent sans hook ne
    # bloque rien et ne le dit pas : c'est exactement le silence qu'on refuse.
    n_hooks = sum(len(b.get("hooks", [])) for bl in d.get("hooks", {}).values() for b in bl)
    if n_hooks:
        rap.append(("+", "%s — %d hooks ancrés sur CLAUDE_PROJECT_DIR, %d deny de périmètre"
                    % (cible.relative_to(projet), n_hooks, len(autres))))
    else:
        rap.append(("⚠", "%s — AUCUN HOOK : pas de briefing, pas de mind-guard, pas de "
                    "journal. Aucune source lisible parmi %s. À câbler à la main."
                    % (cible.relative_to(projet), ", ".join(str(s) for s in sources if s))))
    if appliquer:
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def porte_les_non_herites(projet, cible, appliquer, rap):
    """`.mcp.json` et `settings.local.json` ne remontent PAS depuis un dossier
    d'agent — mesuré le 04/09/2026 sur la conversion de <projet>, horodatage à
    l'appui : un agent démarré dans `agents/<nom>/` ne voyait AUCUN des serveurs
    MCP du projet. Pour `<projet> OPS`, dont tout le lot est `supabase/` et
    `packages/db`, ça voulait dire travailler sans le serveur Supabase.

    Ni l'un ni l'autre n'est suivi par git : on copie, on ne déplace pas, et la
    racine reste la référence pour une session lancée là-bas."""
    for rel in (".mcp.json", ".claude/settings.local.json"):
        src = projet / rel
        if not src.is_file():
            continue
        rap.append(("+", "%s/%s — copié depuis la racine (ne s'hérite pas)"
                    % (cible.relative_to(projet), rel)))
        if appliquer:
            dst = cible / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def migre_memoire_auto(ancien, neuf, appliquer, rap):
    src = HOME / ".claude/projects" / slug(ancien)
    dst = HOME / ".claude/projects" / slug(neuf)
    if not src.is_dir():
        rap.append(("·", "aucune mémoire auto à migrer (%s absent)" % src.name))
        return
    if dst.exists():
        rap.append(("⚠", "%s existe déjà — mémoire auto NON migrée, à fusionner" % dst.name))
        return
    n = len(list(src.glob("*.jsonl")))
    m = len(list((src / "memory").glob("*.md"))) if (src / "memory").is_dir() else 0
    rap.append(("→", "mémoire auto : %s -> %s (%d fils, %d mémoires) ; l'ancien "
                "sera marqué .migre-%s" % (src.name, dst.name, n, m,
                                           datetime.date.today().strftime("%Y%m%d"))))
    if appliquer:
        shutil.copytree(src, dst)
        src.rename(src.with_name(src.name + ".migre-"
                                 + datetime.date.today().strftime("%Y%m%d")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--agents", required=True,
                    help="noms séparés par des virgules ; le PREMIER hérite de l'état existant")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    p = pathlib.Path(a.project_root).resolve()
    noms = [x.strip() for x in a.agents.split(",") if x.strip()]
    rap, reste = [], []

    f, existants = forme(p)
    if f == "ancienne":
        print("Ce projet n'est pas encore migré (.fact/ absent). Lancer d'abord "
              "`migre-fact-docs.py`, puis revenir.")
        return 1
    # Deux agents dont les noms se slugifient pareil partageraient une seule
    # mémoire auto, en silence. C'est irrattrapable une fois installé.
    vus = {}
    for n in noms + existants:
        vus.setdefault(slug(n), []).append(n)
    collisions = [v for v in vus.values() if len(v) > 1]
    if collisions:
        print("REFUS — ces noms donnent la même adresse de mémoire auto : %s. "
              "Ils partageraient une seule mémoire sans que rien ne le dise."
              % " / ".join(", ".join(c) for c in collisions))
        return 1
    hook = p / ".claude/hooks/briefing.py"
    if hook.is_file() and "racines(" not in hook.read_text(encoding="utf-8", errors="replace"):
        print("REFUS — les hooks de ce projet sont d'avant le 04/09/2026 : le "
              "briefing ne fait qu'une remontée et ne verrait jamais `.fact/` "
              "depuis un dossier d'agent. Lancer `/agentic-sync` d'abord.")
        return 1

    if f == "mono":
        premier = noms[0]
        cible = p / "agents" / premier
        rap.append(("→", ".mind/ -> agents/%s/.mind/ (l'agent qui était là garde "
                    "sa mémoire)" % premier))
        if a.apply:
            (cible / ".mind").parent.mkdir(parents=True, exist_ok=True)
            if not git(p, "mv", ".mind", "agents/%s/.mind" % premier):
                shutil.move(str(p / ".mind"), str(cible / ".mind"))
        reglages_agent([p / ".claude/settings.json"], cible / ".claude/settings.json",
                       p, [n for n in noms[1:]], a.apply, rap)
        if (p / ".claude/settings.json").is_file():
            rap.append(("−", ".claude/settings.json de la racine SUPPRIMÉ — il ne "
                        "s'exécute plus (les réglages ne s'héritent pas) et "
                        "quelqu'un l'éditerait un jour en croyant agir sur tous"))
            if a.apply and not git(p, "rm", "-q", ".claude/settings.json"):
                (p / ".claude/settings.json").unlink()
        porte_les_non_herites(p, cible, a.apply, rap)
        migre_memoire_auto(p, cible, a.apply, rap)
        # Le premier agent hérite de l'état, pas d'un rôle : il lui faut le sien,
        # sinon il démarre avec le seul CLAUDE.md du projet et se croit seul.
        rap.append(("+", "agents/%s/CLAUDE.md — rôle à remplir" % premier))
        if a.apply and not (cible / "CLAUDE.md").exists():
            (cible / "CLAUDE.md").write_text(ROLE % premier, encoding="utf-8")
        neufs, tous = noms[1:], noms
        # D'où les agents NEUFS tirent leurs hooks, dans l'ordre. Le settings du
        # premier agent vient d'être écrit et porte déjà les chemins ancrés ; la
        # racine sert de repli en dry-run, où rien n'a encore été supprimé.
        modeles = [p / ".claude/settings.agent.json.example",
                   cible / ".claude/settings.json",
                   p / ".claude/settings.json"]
    else:
        neufs, tous = noms, existants + noms
        modeles = [p / ".claude/settings.agent.json.example"] + [
            p / "agents" / e / ".claude/settings.json" for e in existants]

    for n in neufs:
        d = p / "agents" / n
        rap.append(("+", "agents/%s/ — CLAUDE.md de rôle, settings.json, .mind/ neuf" % n))
        if a.apply:
            (d / ".mind").mkdir(parents=True, exist_ok=True)
            (d / "CLAUDE.md").write_text(ROLE % n, encoding="utf-8")
            (d / ".mind/state.md").write_text(
                "---\nmaj: %s\nsante: vert\njalon: [LE_PROCHAIN_CAILLOU de ce lot]\n---\n\n"
                "# État — %s\n\n[où en est CET agent]\n"
                % (datetime.date.today().isoformat(), n), encoding="utf-8")
            (d / ".mind/todo.md").write_text(
                "# À faire — %s\n\n- [ ] [première tâche de ce lot]\n" % n, encoding="utf-8")
        reglages_agent(modeles, d / ".claude/settings.json", p,
                       [x for x in tous if x != n], a.apply, rap)
        porte_les_non_herites(p, d, a.apply, rap)

    # `.fact/roles.md` — le cinquième fichier, qui n'existe qu'en multi-agents.
    # Le périmètre d'un agent vit dans SON `CLAUDE.md`, que lui seul charge :
    # chacun connaît sa frontière et ignore celle des autres. Constaté en usage,
    # un agent déduisant le périmètre d'un tiers, et un dossier écrit par deux
    # mains sans que personne le sache. On pose le gabarit ; le remplir est une
    # décision, pas une génération.
    fichier_roles = p / ".fact" / "roles.md"
    if (p / ".fact").is_dir() and not fichier_roles.exists():
        rap.append(("+", ".fact/roles.md — qui tient quoi, à remplir"))
        if a.apply:
            gabarit = (pathlib.Path(__file__).resolve().parent.parent
                       / "templates" / "roles.md")
            texte = gabarit.read_text(encoding="utf-8") if gabarit.exists() else \
                    "# Les rôles — %s\n\n| Agent | Tient | Ne touche pas |\n|---|---|---|\n" % p.name
            texte = texte.replace("[PROJECT_NAME]", p.name)
            for i, n in enumerate(tous, 1):
                texte = texte.replace("`<agent-%d>`" % i, "`%s`" % n)
            fichier_roles.write_text(texte, encoding="utf-8")
        reste.append("REMPLIR .fact/roles.md — qui tient quoi, et surtout LES ZONES "
                     "PARTAGÉES. Un périmètre propre se lit dans les deny ; une zone "
                     "partagée ne se lit nulle part, et c'est là que les collisions "
                     "arrivent. C'est de la mémoire `.fact/` : elle s'écrit à la "
                     "demande du commanditaire (` # fact-ok` au commit).")

    reste.append("DÉCOUPER LE CLAUDE.md — la seule étape qui ne s'automatise pas. Le "
                 "commun reste à la racine, le rôle descend dans agents/<nom>/CLAUDE.md. "
                 "Contrôle de sortie : aucune phrase du bas ne resterait vraie pour un "
                 "autre agent.")
    reste.append("ÉCRIRE LES PÉRIMÈTRES en dossiers dans chaque settings.json : les deny "
                 "posés ne couvrent que les dossiers d'agents. Le code, lui, n'est pas "
                 "partagé au hasard — dire qui tient quoi.")
    reste.append("RELANCER LES SESSIONS tmux DANS les dossiers d'agents, sous des noms "
                 "slugifiés (%s). L'ancienne session à la racine n'a plus d'agent : le "
                 "briefing l'avertira au lieu de se taire."
                 % ", ".join(slug(n).lower().strip("-") for n in tous))

    print("── agents — %s (%s)%s" % (p.name, f, "" if a.apply else "  [DRY-RUN]"))
    for signe, ligne in rap:
        print("  %s %s" % (signe, ligne))
    print("\n── À reprendre à la main")
    for r in reste:
        print("  · %s" % r)
    if not a.apply:
        print("\nDry-run. Relancer avec --apply pour écrire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
