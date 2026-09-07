---
name: agentic-agents
description: >
  Convertit un projet MONO-agent en MULTI-agents, ou ajoute un agent à un projet
  qui l'est déjà. Déplace l'état existant dans `agents/<nom>/`, migre la mémoire
  auto (classée par chemin, sinon elle est perdue), repointe les hooks en
  `../../`, pose les périmètres en `deny`. Ne découpe PAS le CLAUDE.md : c'est
  éditorial. Ne convertit pas un projet non migré — `migre-fact-docs.py`
  d'abord. Dry-run par défaut.
  Trigger: /agentic-agents, « passer ce projet en multi-agents », « ajouter un
  agent », « découper ce projet en lots », « ce projet a besoin de deux agents ».
---

# agentic-agents — un projet, plusieurs agents

**Un seul skill, deux comportements, et c'est la forme du projet qui décide.**
Sur un projet mono il convertit ; sur un projet déjà multi il ajoute. Les deux
sont la même opération à une étape près.

> **Avant de découper, lire [`references/roles.md`](references/roles.md).** Ce
> skill pose la mécanique ; il ne choisit pas les rôles, et c'est ce choix qui
> décide de tout le reste. On y trouve les trois rôles types et leurs
> frontières, pourquoi découper par couche technique (back/front) est presque
> toujours faux, ce que le modèle **ne** couvre pas, le seuil au-delà duquel un
> agent seul ne suffit plus, et ce que le multi-agents coûte réellement.
>
> Deux points qui se paient longtemps s'ils sont ratés ici : **le nom d'un rôle
> façonne le comportement de l'agent qui le porte**, et **chaque agent ajouté
> augmente ce qui remonte vers l'humain** — qui reste le seul à pouvoir
> débloquer un lot au profit d'un autre.

À ne pas confondre avec deux voisins :

| | |
|---|---|
| `agentic-team` | la **vue** de l'atelier — lecture seule, ne modifie rien |
| `claude-equipe` | la **délégation** à des ouvriers `claude -p` sur un autre compte |
| **`agentic-agents`** | la **forme** du projet — combien d'agents y travaillent |

Et `agents/` à la racine du projet n'est **pas** `.claude/agents/`, qui est la
convention Claude Code pour les définitions de sous-agents. Plusieurs projets
ont déjà le second ; les deux cohabitent sans se gêner, mais ne pas les mélanger
dans une phrase.

## Quand un projet mérite plusieurs agents

Quand deux lots ont des **rythmes** différents et des **contextes disjoints** —
typiquement fiabilité/infra d'un côté, produit/apps de l'autre. Chacun mérite
alors sa santé, son jalon, sa todo. Un seul agent qui alterne entre les deux
garde une fenêtre à moitié hors sujet.

Ce n'est **pas** une réponse à « le projet est gros ». Un projet gros mais d'un
seul tenant se tient très bien à un agent, et la forme mono coûte moins cher.

## Ce que le script fait

```
.mind/{state,todo}.md   ->  agents/<premier>/.mind/     l'agent qui était là garde sa mémoire
.claude/settings.json   ->  agents/<premier>/.claude/   hooks repointés en ../../
~/.claude/projects/<slug>/  ->  copié vers le slug du dossier d'agent
agents/<autres>/        ->  créés vides, avec rôle, réglages et .mind/ neuf
```

`.fact/`, `docs/`, `.logs/`, le code : **rien ne bouge**. Aucun n'appartient à
un agent.

Le `settings.json` de la racine est **supprimé**. Il ne s'exécute plus — les
réglages ne s'héritent pas, seul celui du dossier de lancement compte — et le
laisser produirait un fichier que quelqu'un éditera un jour en croyant agir sur
tous les agents. La racine ne garde que `.claude/hooks/`, la source unique.

## Le piège qu'il existe pour éviter

**La mémoire auto est classée par CHEMIN.** Convertir déplace le `cwd` de
l'agent de `<projet>/` vers `<projet>/agents/<nom>/`, donc change son slug :
adresse neuve et vide, `--resume` qui ne retrouve rien. Au 04/09/2026 ça
représentait 428 Mo et 20 fils pour <projet>, 58 Mo et 31 mémoires pour <cto>. Le
script migre, ou il refuse.

Il refuse aussi deux noms qui se **slugifient pareil** (`<projet> OPS` et
`<projet>-OPS`) : ils partageraient une seule mémoire auto, en silence, et c'est
irrattrapable une fois installé.

Et il refuse si les hooks du projet sont d'avant le 04/09/2026 : un `briefing`
à une seule remontée ne verrait jamais `.fact/` depuis un dossier d'agent.
`/agentic-sync` d'abord.

## Marche à suivre

```bash
# 1. le projet doit déjà être en forme .fact / docs
python3 .claude/skills/agentic-sync/scripts/migre-fact-docs.py --project-root . --apply

# 2. à blanc, toujours — le premier nommé hérite de l'état existant
python3 .claude/skills/agentic-agents/scripts/agentic-agents.py \
        --project-root . --agents "OPS,PO"

# 3. appliquer
… --apply
```

## Les trois choses qui restent à la main

1. **Découper le `CLAUDE.md`** — la seule étape qui ne s'automatise pas. Le
   commun reste en haut, le rôle descend. Contrôle de sortie : **aucune phrase
   du bas ne resterait vraie pour un autre agent**. Le `CLAUDE.md` du projet est
   chargé à chaque démarrage de chaque agent : une phrase répétée est payée deux
   fois par session.
2. **Écrire les périmètres en dossiers** dans chaque `settings.json`. Le script
   ne pose que les frontières entre dossiers d'agents ; qui tient quel dossier
   de code est une décision. Trois faits mesurés le 04/09/2026, à ne pas
   redécouvrir : seules les règles `Edit(...)` sont évaluées (`Write(...)` est
   inerte) ; un motif **relatif** (`Edit(../autre/**)`) **ne mord pas** ; un
   motif ancré sur le home mord, y compris en `bypassPermissions`.
3. **Relancer les sessions tmux dans les dossiers d'agents**, sous des noms
   slugifiés. L'ancienne session à la racine n'a plus d'agent — le briefing
   l'avertira au lieu de se taire, mais elle ne sert plus à rien.
