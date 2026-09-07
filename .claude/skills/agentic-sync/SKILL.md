---
name: agentic-sync
description: >
  Resynchronise un projet DÉJÀ au harnais sur la dernière version du starter :
  met à jour les fichiers starter-owned (corps des skills, hooks), supprime ce
  que le starter a retiré, applique les renommages, puis réconcilie à la main
  les fichiers project-owned (CLAUDE.md, câblage des hooks, mémoire,
  site.config.yml). Ne touche jamais au contenu de .mind/, docs/, _content/
  ni aux secrets.
  Trigger: /agentic-sync ou "mets mon projet à jour avec le starter".
---

# Agentic Sync

> **Quand l'utiliser** : projet **déjà** au harnais (il a `.claude/skills/`,
> `.mind/` ou `docs/`) qu'on veut remettre au niveau du starter courant.
> Différent d'`agentic-upgrade` (onboarding **additif** d'un projet **sans**
> harnais) et de `project-init` (nouveau projet).


## Migration vers `.fact/` et `docs/` — arrêtée le 04/09/2026

Un projet resté à l'ancienne taxonomie (`.mind/` à cinq fichiers, `.memory/`)
se migre avec le script fourni, **avant** toute autre resynchronisation :

```bash
python3 .claude/skills/agentic-sync/scripts/migre-fact-docs.py --project-root . --apply
```

Il déplace `stack`/`architecture`/`rules` dans `.fact/`, renomme `.memory/` en
`docs/` et `MEMORY.md` en `README.md`, crée `.fact/base.md` en y transportant le
`cap:` qui vivait dans `state.md` — et l'en retire, parce que deux sources pour
un même fait, c'est une qui ment.

**Il ne supprime rien** : `journal.md` (la génération précédente de `.logs/`),
les sorties de build tombées dans `docs/`, les fichiers de trop — il les nomme
et laisse le projet trancher. Supprimer du contenu qu'on n'a pas lu est le geste
qu'on ne rattrape pas.

**Il ne convertit pas en multi-agents** : c'est une autre décision, et elle a
son propre skill, `/agentic-agents`. La forme mono est le défaut.

Après migration, deux choses restent à la main et le script les rappelle : la
section mémoire du `CLAUDE.md`, qui parle encore de cinq fichiers, et le tri de
ce qui traîne dans `docs/`.


## Principe : ownership

- **Starter-owned → mis à jour vers la dernière version** (le script s'en
  charge) : corps des skills (`.claude/skills/**`), scripts des hooks
  (`.claude/hooks/**`), suppression de ce qui a été retiré en amont.
  L'écrasement est **voulu** : c'est le but du sync, récupérer la dernière
  logique.
- **Project-owned → jamais écrasé** : `.mind/**` et `docs/**` (contenu),
  `.claude/settings.json` (permissions **et câblage** des hooks),
  `site/site.config.yml`, `site/_content/**`, `.env*`, `.mcp.json`,
  `settings.local.json`.
- **Zone grise → réconciliée à la main** (étapes 3 à 5), jamais en écrasement
  aveugle : section « Mémoire » et règles de `CLAUDE.md`, câblage des hooks,
  dérive de taxonomie mémoire, et le **moteur de site** (`build_site.py`,
  `publish.py`, `.gitignore`, `_assets/reference.docx`) — le script le
  **signale** s'il diffère mais ne l'écrase jamais : l'écraser seul casserait le
  build tant que `site.config.yml` n'existe pas.

Toujours **dry-run → validation → apply**. Rien de destructif sur le contenu
projet.

## Procédure

### 1. État git

```bash
git status --short
```

Travailler sur une branche dédiée si le projet est en prod
(`git switch -c chore/agentic-sync`).

### 2. Sync mécanique (script)

Dry-run d'abord, depuis la racine du projet :

```bash
python3 .claude/skills/agentic-sync/scripts/agentic-sync.py
```

Sur Windows, l'interpréteur s'appelle `python`. Si le projet n'a pas encore ce
skill, lancer depuis un clone local du starter :

```bash
python3 <CHEMIN_STARTER>/.claude/skills/agentic-sync/scripts/agentic-sync.py --project-root <CHEMIN_PROJET>
```

Présenter le rapport (Changements / À réconcilier à la main). Après accord :

```bash
python3 .claude/skills/agentic-sync/scripts/agentic-sync.py --apply
```

Le script met les skills et les hooks en miroir (ajoute les nouveaux, met à jour
les corps, supprime ce qui a été retiré en amont), signale le moteur de site
sans l'écraser, et supprime les chemins obsolètes ou renommés. Il ne crée pas de
`site/` là où il n'y en a pas (→ `/publish-docs init`).

### 3. Câbler les hooks — l'étape qu'on oublie

Le script a mis à jour les **scripts** des hooks. Il n'a pas touché à
`settings.json`, qui est project-owned : un hook fraîchement copié peut n'être
branché nulle part. **Un hook non câblé ne fait rien et ne le dit
pas** — c'est exactement ce qui est arrivé à `memory-guard`, déclaré `python` et
silencieux pendant des mois sur une machine où seul `python3` existe.

Vérifier que `settings.json` du projet déclare, comme celui du starter :

- `mind-guard.py` en **`PreToolUse`** sur `Bash(git commit*)`
- `journal.py` en **`PostToolUse`** sur `Bash(git commit*)`
- `attente.py` en **`Stop`**, sans matcher — il se déclenche à chaque fin de
  tour, pas sur une commande
- chacun **deux fois**, une entrée `python` et une entrée `python3`, pour
  couvrir Windows et macOS sans opérateur de shell.

Un projet déjà au harnais **n'a pas** le `Stop` : il est arrivé après. Le poser
est le point le plus facile à oublier d'une resynchro, et son absence ne se voit
pas — un hook non câblé ne fait rien et ne le dit pas.

Un dépôt **multi-domaines** pose `mind-guard-relais.py` dans les
sous-périmètres : il remonte à la racine par `git rev-parse`, sans compter les
dossiers.

### 4. Réconcilier `CLAUDE.md` (guidé, pas d'écrasement)

Comparer avec le `CLAUDE.md` du starter **uniquement sur les sections
structurelles**, sans toucher au rôle ni aux règles métier du projet :

- **Section « Mémoire projet »** : aligner sur les trois dossiers, trois natures —
  `.fact/` = faits du projet, quatre fichiers (cinq en multi-agents, avec
  `roles.md`), le texte périmé s'y
  **remplace** ; `docs/` = traces datées, ça s'accumule. Et les deux hooks.
- **Règles** : si une règle générique a évolué dans le template, proposer le
  diff.

Montrer chaque changement, appliquer après validation.

### 5. Mémoire : proposer le CHOIX, ne rien migrer d'office

Le script ne touche jamais au contenu. S'il détecte une taxonomie d'avant le
02/09/2026 — `state.md`, `rules.md` ou `architecture.md` encore dans `docs/`,
un `charter.md`, un `business.md` — il le **signale**. Poser le choix :

- **(A) Garder la taxonomie actuelle.** Rien n'est modifié. Limite, et elle est
  concrète : le tableau de bord lit `.mind/state.md` et `.mind/todo.md`. Sans
  eux, **le projet n'apparaît pas** — pas en erreur, absent.
- **(B) Migrer.** C'est un **TRI**, pas une création : les fichiers de faits
  actuels **montent** dans `.mind/`, les traces datées **restent** dans
  `docs/`.

Ne migrer **que si l'utilisateur choisit (B)**, et de façon **non destructive** :
copier vers la nouvelle place, faire relire, supprimer les originaux seulement
après validation explicite.

| Ancien | → |
|---|---|
| `docs/state.md`, `rules.md`, `architecture.md` | **montent** dans `.mind/` |
| `business.md` (règles, contraintes) | `.fact/rules.md` |
| `business.md` (domaine, frontières, rôles) | `.fact/architecture.md` |
| `business.md` (stack, outils, environnements) | `.fact/stack.md` |
| `charter.md` | se **dissout** : but → champ `cap:` de `.mind/state.md`, rôle → `CLAUDE.md`, frontières → `.fact/architecture.md` |
| `clients.md`, `overview.md` | se dissolvent ; le contractuel et le nominatif vont dans `docs/operations.md` (🔒) |
| `hosting.md`, `troubleshooting.md`, secrets | `docs/operations.md` (🔒 privé) |
| `todo.md` | `.mind/todo.md`, au dialecte du tableau de bord (`[ ]`/`[>]`/`[x]`, `!haut`, `@<qui>`) |
| `data-model.md` | garder si data-lourd, sinon fondre dans `.fact/architecture.md` |
| `decisions.md` | **reste** dans `docs/` — c'est daté |

Le test qui tranche : une phrase qui commence par « on a décidé de », ou qui
porte une date au passé, va dans `docs/`. Le reste va dans `.mind/`.
**Jamais un sixième fichier dans `.mind/`.**

**Multi-domaine** : `.mind/` reste **à la racine du dépôt**, jamais à un niveau
intermédiaire — c'est ce que lit le tableau de bord, et il n'en cherche qu'un.
Les sous-périmètres portent leur `CLAUDE.md` et leur `docs/` ; leur état
remonte dans le `.mind/state.md` de la racine.

Finir en vérifiant que `.mind/state.md` porte un en-tête complet (`maj`, `cap`,
`sante`, `jalon`, avec `maj` à la date du jour) et que `docs/README.md`
pointe la bonne liste.

### 6. Site : hardcodé → config-driven (si applicable)

Si le projet a un `site/` **sans** `site.config.yml`, le moteur a été signalé
comme divergent à l'étape 2. Le migrer dans ce bloc : swap du moteur, puis
créer `site/site.config.yml` (`title`, `tagline`, `logo_letter`, `preset`,
`deploy`), vérifier `_content/` et les `_diagrams/`, et exiger que
`python site/publish.py --no-deploy` reproduise le site sans perte.
Si `site/` est absent : `/publish-docs init`, ou ne rien faire.

### 7. Contrôles

```bash
# plus aucune référence aux éléments retirés ou aux anciens noms
rg --hidden -n -i "\.claude/agents|\.codex|AGENTS\.md|agent-init|doc-site|project-upgrade|memory-guard|memory-update" --glob '!.git/**'
# secrets : la mémoire publique et _content ne fuitent rien
rg -n -iE "(BEGIN PRIVATE|AccountKey|SAS=|[0-9]{1,3}(\.[0-9]{1,3}){3})" .mind .memory site/_content 2>/dev/null
```

Puis un contrôle qui vaut mieux qu'une lecture : faire un commit de test et
vérifier que `mind-guard` réagit, et que `.logs/<jour>.md` s'écrit. Pour
`attente`, modifier un fichier de code sans toucher `.mind/todo.md` et finir un
tour : l'agent doit être renvoyé au travail. Un hook qu'on n'a pas vu se
déclencher n'est pas un hook vérifié.

## Règles

- Ne jamais écraser `.mind/**`, `docs/**`, `site/_content/**`,
  `site/site.config.yml`, `.env*`, `settings.json` ni les settings locaux.
- Ne jamais supprimer de contenu mémoire sans confirmation explicite : migration
  = copie, relecture, puis retrait validé.
- Un seul harnais, `.claude/`, et un seul assistant. Un dépôt qui porte encore
  `.codex/`, un `AGENTS.md` ou un `memory-guard.py` est en retard : le script
  les supprime, ne jamais les recréer.
- Rapporter ce qui a été synchronisé, supprimé, et ce qui reste à réconcilier.
  Ne rien voir n'est pas un succès, c'est une absence de mesure.
- Projet en prod : brancher (`git switch -c`), un commit par bloc — mécanique,
  hooks, mémoire, site.
