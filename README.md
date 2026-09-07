# claude-starter

> Le harnais d'un projet piloté par Claude Code : une architecture mémoire qui
> tient dans le temps, des skills, des permissions, un site de doc optionnel.

**Un seul harnais, un seul assistant : Claude Code.** Le starter en a porté un
second en miroir jusqu'au 3 septembre 2026. Le maintenir à l'identique était une
discipline que rien n'appliquait : les deux copies divergeaient en silence.

Le parti pris tient en une phrase : **poser une architecture saine sans être
compliqué.** Ce qui est une brique d'architecture de projet reste ici ; ce qui
relève de l'exploitation d'une machine n'y est pas.

---

## La méthode, d'un coup d'œil

```
  ┌─ UNE FOIS PAR MACHINE ──────────────────────────────────────────────┐
  │   ① INSTALLER L'ATELIER          la méthode + le poste du pilote    │
  └────────────────────────────────┬────────────────────────────────────┘
                                   │
  ┌─ UNE FOIS PAR PROJET ──────────┼────────────────────────────────────┐
  │                                ▼                                    │
  │   ② MONTER LE PROJET      neuf ? existant ? déjà au harnais ?       │
  │                           puis : UN agent, ou PLUSIEURS ?           │
  │                                │                                    │
  │                       ┌────────┴────────┐                           │
  │                     MONO             MULTI                          │
  │                       │                 │                           │
  │                       │        ③ DÉCOUPER EN AGENTS                 │
  │                       │           OPS · PO · AUDIT                  │
  │                       │           tout le monde lit tout,           │
  │                       │           seule l'écriture est découpée     │
  │                       └────────┬────────┘                           │
  │                                ▼                                    │
  │   ④ ÉCRIRE LES CLAUDE.md   avant de leur parler — 4 niveaux,        │
  │                            et le settings.json n'est PAS hérité     │
  └────────────────────────────────┬────────────────────────────────────┘
                                   │
  ┌─ À CHAQUE ÉCHANGE ─────────────┼────────────────────────────────────┐
  │                                ▼                                    │
  │   ⑤ LE WORKFLOW      il relit sa mémoire ─► il travaille ─►         │
  │                      REFUSÉ s'il commite sans état à jour ─►        │
  │                      REFUSÉ s'il rend la main sans noter            │
  │                      ce qui t'attend                                │
  │                                │                                    │
  │   ⑥ LA BOUCLE        ses blocages arrivent sur ton téléphone ;      │
  │                      tu coches, la décision repart vers l'agent     │
  │                                │                                    │
  │   ⑦ LA MÉMOIRE       .fact/ les faits · .mind/ l'état · docs/ les   │
  │                      traces · .logs/ le journal automatique         │
  └─────────────────────────────────────────────────────────────────────┘

        LES DEUX REFUS DE ⑤ SONT TOUT LE SYSTÈME.
        Pas des consignes — des blocages. On a mesuré que la prose
        ne suffit pas.
```

**Chaque phase a son schéma dans [`SCHEMAS.md`](SCHEMAS.md)**, avec les six
pièges qui coûtent une demi-journée à qui les découvre seul.

**Ce README ne réexplique rien de tout ça.** Il ne contient que ce qu'un schéma
ne peut pas porter : **les commandes à taper**, les prérequis, et les points
d'exploitation.

| Fichier | Ce qu'il contient | Quand l'ouvrir |
|---|---|---|
| [`SCHEMAS.md`](SCHEMAS.md) | la méthode **en schémas** — la forme, l'ordre, ce qui bloque quand | pour **comprendre** |
| ce `README.md` | ce qu'on **tape** — installation, prérequis, MCP, RTK | pour **faire** |
| **[`templates/foundation-CLAUDE.md`](.claude/skills/agentic-init/templates/foundation-CLAUDE.md)** | **LA MÉTHODE, en entier et normative** — c'est le fichier que les agents lisent | quand un détail **fait autorité** |
| `.claude/skills/*/SKILL.md` | le mode d'emploi détaillé d'**un** outil | quand l'agent le lance |

Le template du socle n'est pas un document interne : c'est **le fichier qui est
copié** en `~/Agentic/CLAUDE.md` par `/agentic-init`, et que tout agent ouvert
dans un sous-dossier lit à chaque session. Le lire, c'est lire ce que les agents
lisent.

`SCHEMAS.md` ne le double pas : **il n'énonce aucune règle qui n'existe pas
ailleurs**, il en donne la forme. Deux textes qui énonceraient les mêmes règles
divergeraient sans que personne le voie ; un plan et un règlement, non. En cas
d'écart, **le socle fait foi**.

---

## Machine neuve — monter l'atelier d'abord

Le starter monte **un projet**. Avant le premier projet, sur une machine neuve,
on monte l'**atelier** : la couche au-dessus. → [`SCHEMAS.md`, phase 1](SCHEMAS.md#phase-1--installer-latelier)

### La bonne façon : le faire faire à un agent

Le `SKILL.md` d'`agentic-init` est **écrit pour être suivi par un agent**, pas lu
par un humain. Autant s'en servir.

**Où ouvrir la session — c'est le seul piège de toute la procédure.** Créer
`~/Agentic`, et y ouvrir l'agent **là** ; pas dans `~/Agentic/cto`, qui n'existe
pas encore et que le script crée lui-même. Le socle va **un niveau au-dessus** du
dossier du CTO : posé à l'intérieur, il ne serait lu que par le CTO et **aucun
projet n'en hériterait**. Aucune erreur ne le signalerait, la méthode serait
simplement sans effet.

Puis coller ceci :

```text
Monte l'atelier agentique sur cette machine.

1. Clone le starter à côté, PAS ici :
   git clone https://github.com/<compte>/claude-starter.git /tmp/claude-starter

2. Lis /tmp/claude-starter/.claude/skills/agentic-init/SKILL.md et suis-le.
   Racine = ce dossier, CTO = `cto` en minuscules, utilisateur = <prénom>.

3. Lance le script en DRY-RUN d'abord et montre-moi le rapport.
   N'applique rien avant que je te le dise.

4. Après --apply, deux choses que le script ne fait pas et que j'attends de toi :
   - remplis .mind/state.md et .mind/todo.md du CTO. Ils arrivent en template
     avec `maj: YYYY-MM-DD` : tant qu'ils sont vides, mind-guard refusera le
     premier commit et le briefing annoncera « EN-TÊTE ILLISIBLE ». C'est voulu.
   - prouve les hooks : un commit d'essai de code sans toucher .mind/ doit être
     REFUSÉ, puis .logs/<jour>.md doit s'écrire au commit suivant. Un hook qu'on
     n'a pas vu se déclencher n'est pas un hook vérifié.

5. Quand tout est en place, PRÉVIENS-MOI explicitement et arrête-toi là :
   dis-moi que l'atelier est monté, donne-moi le chemin exact où rouvrir une
   session (~/Agentic/cto), et rappelle-moi pourquoi il faut changer de dossier.
   Ne monte aucun projet depuis ici — c'est le travail du CTO, depuis chez lui.
```

Le prompt **pointe le `SKILL.md`** au lieu de recopier ses étapes. Une copie se
périmerait le jour où le skill change, et personne ne le verrait.

> **Le nom du dossier est une adresse.** `cto` en minuscules, décidé une fois
> pour toutes : la mémoire auto de Claude Code est indexée par le **chemin de
> travail**. Renommer le dossier plus tard l'orpheline en entier, transcripts
> compris, **sans afficher la moindre erreur**.

### À la main

```bash
git clone https://github.com/<compte>/claude-starter.git /tmp/claude-starter
python3 /tmp/claude-starter/.claude/skills/agentic-init/scripts/agentic-init.py \
        --racine ~/Agentic --cto cto --utilisateur <prénom>
# lire le rapport, puis relancer avec --apply
```

Sur Windows, l'interpréteur s'appelle `python`, et le dossier temporaire
`$env:TEMP\claude-starter`.

### Prérequis, dans l'ordre où ils bloquent

| | Pourquoi |
|---|---|
| **Python** | dépendance dure — les cinq hooks en ont besoin. `python` sur Windows, `python3` sur macOS. |
| **git** | sans dépôt, `mind-guard`, `journal` et `attente` sont **inertes** — et ne le disent pas. |
| **un compte Claude Code** | avec l'isolation qui convient si la machine en sert plusieurs. |

---

## Quickstart — projet neuf

**1. Cloner dans le projet**

```bash
git clone https://github.com/<compte>/claude-starter.git .
```

**2. Recharger l'éditeur** — `Shift + Ctrl + P` → **Developer: Reload Window**,
pour que Claude Code voie les nouveaux fichiers.

**3. Initialiser**

```text
/project-init
```

L'agent scanne le projet et pose sept questions — **la première étant « un agent,
ou plusieurs ? »**, parce qu'elle décide de l'emplacement du `.mind/` et du chemin
d'appel des hooks. → [`SCHEMAS.md`, phase 2](SCHEMAS.md#phase-2--monter-un-projet)

**4. Coder.** La mémoire se tient toute seule.

---

## Projet existant

Un projet qui porte déjà du code ne passe pas par `/project-init`, réservé à un
projet neuf. Le skill dédié est **`/agentic-upgrade`**, purement **additif**
(*copy-if-missing*, aucun écrasement).

Le skill vivant dans `.claude/`, il faut amorcer le harnais d'abord :

```bash
# macOS / Linux
git clone https://github.com/<compte>/claude-starter.git /tmp/claude-starter
cp -r /tmp/claude-starter/.claude ./
rm -rf /tmp/claude-starter
# recharge l'éditeur, puis dans Claude Code : /agentic-upgrade
```

```powershell
# Windows PowerShell
git clone https://github.com/<compte>/claude-starter.git $env:TEMP\claude-starter
Copy-Item -Recurse "$env:TEMP\claude-starter\.claude" ".\.claude"
Remove-Item -Recurse -Force "$env:TEMP\claude-starter"
# recharge (Shift+Ctrl+P → Developer: Reload Window), puis : /agentic-upgrade
```

> Projet **déjà** au harnais, à remettre au niveau de la dernière version →
> `/agentic-sync`.

---

## Ce qu'il y a dans la boîte

### Les neuf skills

| Skill | Ce qu'il fait | Quand |
|---|---|---|
| `agentic-init` | monte l'**atelier** : socle de méthode + poste du CTO | une fois par machine |
| `project-init` | initialise un **nouveau** projet | dossier vide |
| `agentic-upgrade` | onboarde un projet **sans** harnais — additif pur | du code, pas de harnais |
| `agentic-sync` | resynchronise un projet **déjà** au harnais. Porte `migre-fact-docs.py` pour l'ancienne taxonomie (`.mind/` à cinq fichiers, `.memory/`) | mise à niveau |
| `agentic-agents` | **convertit** mono → multi, ou **ajoute** un agent. Ne découpe pas le `CLAUDE.md` : c'est éditorial | découpage |
| `agentic-team` | **lit** l'état de tous les projets et rend un diagnostic terminal + une page HTML autonome. Strictement en lecture | « où en est l'équipe ? » |
| `agentic-clean` | supprime les caches régénérables en écrivant la commande qui les refait ; **signale sans y toucher** les résidus et la mémoire hypertrophiée. Dry-run par défaut | le disque est plein |
| `publish-docs` | site Quarto (HTML + Word/PDF) depuis la mémoire **publique**. **Ne lit jamais** `operations.md` ni les `.env*` | documenter |
| `caveman` | mode ultra-compressé. **Jamais sur `.mind/todo.md` ni les `.logs/`** — la compression fusionne les listes, et les priorités disparaîtraient sans erreur | réduire les jetons |

### Le harnais

| Fichier | Rôle |
|---|---|
| `CLAUDE.md` | le contexte projet, chargé à chaque session |
| `.claude/settings.json` | permissions et câblage des hooks. **En multi-agents, celui de la racine n'existe pas** — il ne s'exécuterait pas |
| `.claude/settings.agent.json.example` | le gabarit d'un agent : cinq hooks appelés en `../../`, périmètre en `deny` |
| `.claude/settings.local.json.example` | ajustements locaux, non commités |
| `.claude/hooks/` | les cinq hooks → [`SCHEMAS.md`, phase 5](SCHEMAS.md#phase-5--le-workflow-dun-échange) |
| `.claude/hooks/mind-guard-relais.py` | pour un dépôt **multi-domaines** : chaque sous-périmètre le pose à la place du hook, et il remonte à la racine par `git rev-parse` — sans compter les dossiers, donc sans casser à la première réorganisation |
| `.fact/` `.mind/` `docs/` `.logs/` | la mémoire → [`SCHEMAS.md`, phase 7](SCHEMAS.md#phase-7--la-mémoire) |
| `site/` | moteur Quarto, piloté par `site/site.config.yml` |
| `.rtk/filters.toml` | filtres RTK propres au dépôt (voir plus bas) |

---

## Configuration MCP

```bash
cp .mcp.json.example .mcp.json          # macOS / Linux
```

```powershell
Copy-Item .mcp.json.example .mcp.json   # Windows
```

## Permissions locales

Les permissions partagées sont dans `.claude/settings.json`. Pour des ajustements
locaux non commités :

```bash
cp .claude/settings.local.json.example .claude/settings.local.json
```

```powershell
Copy-Item .claude/settings.local.json.example .claude/settings.local.json
```

---

## Portabilité

Le starter tourne sur **macOS et Windows**, en une seule version — jamais deux
variantes. Deux conséquences concrètes :

- **Python est une dépendance dure.** Le nom de l'interpréteur diffère (`python`
  sur Windows, `python3` sur macOS), c'est pourquoi les hooks sont déclarés
  **deux fois** dans le gabarit d'agent. Celle dont l'interpréteur manque échoue
  au démarrage, sans sortie donc sans décision. **Exception : le hook `Stop`**,
  déclaré une seule fois avec repli — un double appel pousserait deux fois vers
  le canal du commanditaire.
- **Aucun script propre à un OS** : ni PowerShell seul, ni shell POSIX seul. Un
  outil qu'une des deux machines ne peut pas lancer ne signale jamais qu'il est
  mort.

## RTK — réduire les jetons dépensés en sortie de shell

[RTK](https://github.com/rtk-ai/rtk) est un binaire Rust qui intercepte la sortie
des commandes shell et la compresse avant qu'elle n'atteigne le contexte de
l'agent : annoncé à **60-90 %** de moins sur les commandes de développement
courantes. Il couvre une centaine de commandes — `git`, `ls`, `grep`, `find`,
`docker`, `kubectl`, `pytest`, `cargo`, `gh`…

**Le binaire ne fait pas partie du starter, et c'est délibéré.** Il s'installe sur
la **machine**, une fois pour toutes les sessions ; le starter pose l'architecture
d'un **projet**.

```bash
brew install rtk        # macOS ; Linux : curl -fsSL .../install.sh | sh
rtk init -g             # câble le hook de réécriture, puis redémarrer Claude Code
```

Windows a un binaire natif (≥ 0.37.2). Sur macOS et Linux, le hook de RTK est un
script bash qui a besoin de **`jq`** et de **`rg`** ; sans eux il prévient sur
`stderr` et se retire — il ne casse rien.

Ce qui appartient au projet, en revanche, est **`.rtk/filters.toml`** : les
filtres propres à ce dépôt, commités, qui surchargent les filtres globaux. Le
starter le fournit, commenté. Sans RTK installé il est inerte.

> Ne pas écrire de filtres à l'avance. Laisser tourner, puis `rtk gain` dit
> **quelles** commandes coûtent vraiment. Un filtre écrit d'avance compresse du
> bruit imaginaire.

### Ce que RTK change pour les hooks — à lire avant de l'installer

RTK réécrit `git commit` en `rtk git commit`, et son hook renvoie un
`permissionDecision: "allow"` accompagné du `updatedInput`. Deux hooks du starter
se déclenchent précisément sur `git commit`. D'où deux points de contact :

1. **Les déclencheurs** — `mind-guard` et `journal` sont déclarés sur
   `Bash(git commit*)` **et** sur `Bash(rtk git commit*)`. Sans quoi un hook
   parfaitement sain cesserait de se déclencher le jour où quelqu'un installe
   RTK, sans rien dire.
2. **Le verrou git** — la liste `deny` couvre aussi `rtk git commit*` et
   `rtk git push*`, sinon la réécriture suffisait à le contourner.

**Ce qui n'est pas mesuré, et qu'il faut mesurer une fois.** L'ordre entre le hook
global de RTK et les hooks du projet n'a pas été vérifié : si RTK réécrit la
commande **avant** que `mind-guard` ne la voie, c'est le déclencheur
`rtk git commit*` qui joue ; sinon c'est l'autre. Les deux sont posés, donc le cas
est couvert dans les deux sens — mais **le seul contrôle qui vaut est un commit
d'essai** : tenter un commit de code sans toucher à `.mind/`, et vérifier que
`mind-guard` refuse toujours et que `.logs/<jour>.md` s'écrit toujours. Un hook
qu'on n'a pas vu se déclencher n'est pas un hook vérifié.

## Contribuer

Tout passe par des **skills**, dans `.claude/skills/`. Garde la mémoire dans
`.fact/`, `.mind/` et `docs/`, à la racine du projet : elle appartient au projet,
pas au harnais.
