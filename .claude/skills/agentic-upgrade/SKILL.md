---
name: agentic-upgrade
description: >
  Onboarde un projet existant qui n'a PAS encore le harnais (ou est resté sur
  l'ancien `.claude/memory/`) : pose `.mind/`, `docs/`, les skills et les
  hooks, en additif, sans écraser les personnalisations. Pour un projet DÉJÀ au
  harnais qu'on veut remettre au niveau du starter, utiliser `agentic-sync`.
---

# Agentic Upgrade

> **Quand l'utiliser** : projet existant **sans** harnais (aucun `.mind/`, ou
> ancien `claude-starter` avec `.claude/memory/`). Purement **additif** :
> *copy-if-missing*, jamais d'écrasement, aucune suppression.
> Projet **déjà** au harnais, à remettre au niveau du starter courant → c'est
> `agentic-sync`, pas ce skill.

## Objectif

- conserver `.claude/` et `CLAUDE.md` tels qu'ils sont
- poser `.fact/` (les quatre fichiers), `.mind/` (les deux) et `docs/`
- remonter la mémoire de `.claude/memory/` vers `docs/`
- poser les deux hooks (`mind-guard`, `journal`) et les skills manquants
- ne jamais écraser un fichier personnalisé sans le signaler

## Procédure

1. Lire l'état Git avant toute action — le script écrit dans l'arbre de travail :

   ```bash
   git status --short
   ```

2. Lancer le script en **dry-run** depuis la racine du projet à migrer :

   ```bash
   python3 .claude/skills/agentic-upgrade/scripts/agentic-upgrade.py
   ```

   Sur Windows, l'interpréteur s'appelle `python`. Si le projet n'a pas encore
   ce skill, lancer le script depuis un clone local du starter :

   ```bash
   python3 <CHEMIN_STARTER>/.claude/skills/agentic-upgrade/scripts/agentic-upgrade.py --project-root <CHEMIN_PROJET>
   ```

3. Présenter le rapport à l'utilisateur — d'abord la section **« À reprendre à
   la main »**, c'est celle qui demande une décision.

4. Appliquer seulement après accord :

   ```bash
   python3 .claude/skills/agentic-upgrade/scripts/agentic-upgrade.py --apply
   ```

   Pour supprimer l'ancien `.claude/memory/` une fois copié vers `docs/`,
   ajouter `--remove-legacy-memory`. Sans ce drapeau, l'ancien dossier reste :
   deux copies valent mieux qu'une perte.

5. Faire le travail de jugement (sections ci-dessous), puis contrôler qu'il ne
   reste rien de l'ancien monde :

   ```bash
   rg --hidden -n "\.claude/memory|claude-starter|AGENTS\.md|memory-guard" --glob '!.git/**'
   ```

## Ce que le script ne fait pas — et pourquoi

Le script pose des fichiers. Il ne **trie** rien, parce que trier demande de
lire le contenu, et le contenu appartient au projet. Trois travaux restent à
l'agent, dans cet ordre :

### 1. La mémoire — c'est un TRI, pas une création

Les templates `.mind/` viennent d'être posés **vides**, à côté d'une mémoire qui
existe déjà. Le travail est de faire **monter** le contenu, pas d'en écrire un
nouveau. Trois dossiers, trois natures : `.fact/` n'énumère que des **faits
actuels** (le texte périmé s'y **remplace**), `docs/` garde les **traces
datées** (ça s'accumule).

| Ancien | → |
|---|---|
| `docs/state.md`, `rules.md`, `architecture.md` | **montent** dans `.mind/` — mêmes noms |
| `business.md` (règles métier, contraintes) | `.fact/rules.md` |
| `business.md` (domaine, frontières, rôles) | `.fact/architecture.md` |
| `business.md` (stack, outils, environnements) | `.fact/stack.md` |
| `charter.md` | se **dissout** : le but → champ `cap:` de `.mind/state.md`, le rôle → `CLAUDE.md`, les frontières → `.fact/architecture.md` |
| `clients.md` | se dissout ; ce qui est contractuel ou nominatif va dans `docs/operations.md` (🔒 privé) |
| `decisions.md` | **reste** dans `docs/` — c'est daté, c'est une trace |
| hébergement / secrets / dépannage, souvent épars | `docs/operations.md` (🔒 privé) |
| `data-model.md` | garder si le projet est data-lourd, sinon fondre dans `.fact/architecture.md` et supprimer |

Le test qui tranche : une phrase qui commence par « on a décidé de », ou qui
porte une date au passé, va dans `docs/`. Tout le reste va dans `.mind/`.

**Jamais un sixième fichier dans `.mind/`.** S'il n'y rentre pas, il est à
`docs/`.

Une fois le contenu remonté, supprimer les originaux — après confirmation de
l'utilisateur, jamais d'office. Vérifier enfin que `.mind/state.md` porte un
en-tête complet (`maj` / `cap` / `sante` / `jalon`, `maj` à la date du jour) :
c'est ce que lit le tableau de bord, et un en-tête cassé fait sortir le projet
du tableau **sans bruit**.

### 2. `settings.json` — le câblage des hooks

Les hooks ont été **copiés**, mais un projet qui avait déjà un `settings.json`
garde le sien : les hooks y sont peut-être branchés nulle part. Un hook qui ne
est pas câblé ne fait rien **et ne le dit pas**. Recopier le bloc `hooks` du
`settings.json` du starter — `mind-guard` en `PreToolUse`, `journal` en
`PostToolUse`, chacun **déclaré deux fois** (`python` et `python3`) pour couvrir
Windows et macOS.

### 3. `CLAUDE.md`

Jamais écrasé. Y réconcilier le rôle, les règles, et la section Mémoire qui
décrit les deux dossiers et les deux hooks.

## Site de documentation (optionnel)

Si le projet n'a pas de dossier `site/`, proposer `/publish-docs init` puis
`/publish-docs refresh` : une doc Quarto (HTML + Word/PDF) générée depuis la
mémoire **publique**. `operations.md` n'est jamais lu.

## Règles

- Ne rien supprimer, sauf `.claude/memory/` avec `--remove-legacy-memory`, et
  seulement une fois la copie faite.
- Ne pas écraser `CLAUDE.md`, `.mind/`, `docs/`, ni un `settings.json`
  existant.
- Si `.claude/memory/` **et** `docs/` existent tous les deux, ne pas
  fusionner automatiquement : signaler, laisser l'utilisateur trancher.
- Un `.codex/`, un `AGENTS.md`, un `memory-guard.py` trouvés dans le projet sont
  les restes d'une version antérieure du starter, retirés le 03/09/2026 : les
  signaler, ne jamais les recréer. C'est `/agentic-sync` qui les supprime.
- Rapporter ce qui a été ajouté, ce qui a été ignoré, et ce qui reste à faire —
  ne rien voir n'est pas un succès, c'est une absence de mesure.
