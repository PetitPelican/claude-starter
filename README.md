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

## Où la méthode est écrite

Trois fichiers, et un seul est la référence. À n'en lire qu'un, c'est le
premier.

| Fichier | Ce qu'il contient | Pour qui |
|---|---|---|
| **[`templates/foundation-CLAUDE.md`](.claude/skills/agentic-init/templates/foundation-CLAUDE.md)** | **LA MÉTHODE, en entier** — mémoire, hooks, skills, délégation, frontières, réflexes | l'agent, et le lecteur |
| ce `README.md` | comment **installer**, et ce que le dépôt **contient** | le lecteur, à l'arrivée |
| `.claude/skills/*/SKILL.md` | le mode d'emploi détaillé d'**un** outil | l'agent, quand il le lance |

Le template du socle n'est pas un document interne : c'est **le fichier qui est
copié** en `~/Agentic/CLAUDE.md` par `/agentic-init`, et que tout agent ouvert
dans un sous-dossier lit ensuite à chaque session. Le lire, c'est lire ce que
les agents lisent. Il n'y a pas de version « pour humains » à côté, et c'est
délibéré : deux versions divergeraient, et personne ne le verrait.

Ce README, lui, ne réexplique pas la méthode — il dit ce qu'il y a dans la
boîte et comment s'en servir.

---

## Machine neuve — monter l'atelier d'abord

Le starter monte **un projet**. Avant le premier projet, sur une machine neuve,
on monte l'**atelier** : la couche au-dessus.

Ça pose deux choses, et rien d'autre :

- **`~/Agentic/CLAUDE.md`** — la **méthode**, héritée par tout agent ouvert dans
  un sous-dossier. C'est l'artefact qui se transporte d'une machine à l'autre.
- **`~/Agentic/cto/`** — le poste du CTO : harnais complet, mémoire, dépôt git.
  Il sait ensuite monter les projets un par un.

### La bonne façon : le faire faire à un agent

Le `SKILL.md` d'`agentic-init` est **écrit pour être suivi par un agent**, pas
lu par un humain. Autant s'en servir.

**Où ouvrir la session — c'est le seul piège de toute la procédure.** Créer
`~/Agentic`, et y ouvrir l'agent **là** ; pas dans `~/Agentic/cto`, qui n'existe
pas encore et que le script crée lui-même. Le socle va **un niveau au-dessus**
du dossier du CTO : posé à l'intérieur, il ne serait lu que par le CTO et
**aucun projet n'en hériterait**. Aucune erreur ne le signalerait, la méthode
serait simplement sans effet.

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
périmerait le jour où le skill change, et personne ne le verrait — c'est la même
raison qui fait qu'il n'existe pas de version « pour humains » du socle.

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

Trois couches, une seule voyage :

| Couche | Fichier | Portable ? |
|---|---|---|
| Poste | `~/.claude/CLAUDE.md` — comptes, sessions, réseau | non, refait par machine |
| **Méthode** | **`~/Agentic/CLAUDE.md`** — mémoire, hooks, skills, frontières | **oui** |
| Projet | `<projet>/CLAUDE.md` — rôle, stack, règles métier | non, propre au projet |

Le socle ne « prévaut » pas sur les `CLAUDE.md` de projet : les deux sont lus, et
le plus spécifique l'emporte. Il porte donc l'invariant, pas des surcharges.
Détail dans `/agentic-init`.

---

## Un agent, ou plusieurs ?

C'est le premier choix, et `/project-init` le pose en **première** question —
parce qu'il décide de l'emplacement du `.mind/` et du chemin d'appel des hooks.

**La réponse n'engage à rien** : la conversion est un appel de skill
(`/agentic-agents`), il n'y a pas à deviner juste au premier jour. Défaut :
mono.

```
MONO — un agent, à la racine                MULTI — plusieurs agents
projet/                                     projet/
  CLAUDE.md      méthode + rôle               CLAUDE.md      le strict commun
  .fact/         4 fichiers                   .fact/         4 fichiers
  docs/          les traces                   docs/          les traces
  .logs/         le journal                   .logs/         le journal
  .mind/         state · todo                 .claude/hooks/ source unique
  .claude/       settings + hooks             src/ …
  src/ …                                      agents/
                                                ops/  CLAUDE.md · .claude/ · .mind/
                                                po/   CLAUDE.md · .claude/ · .mind/
```

**Trois éléments par agent** — son `CLAUDE.md` de rôle, son
`.claude/settings.json` (hooks + périmètre), son `.mind/`. Rien d'autre :
`.fact/`, `docs/`, `.logs/` et le code n'appartiennent à aucun agent.

Quand un projet mérite d'être coupé : quand deux lots ont des **rythmes**
différents et des **contextes disjoints** — typiquement infra/fiabilité d'un
côté, produit/apps de l'autre. Ce n'est pas une réponse à « le projet est
gros » : un projet gros mais d'un seul tenant se tient très bien à un agent.

**Trois faits mesurés qui expliquent la forme**, et qu'il vaut mieux ne pas
redécouvrir :

- le `CLAUDE.md` du projet **est hérité** par un agent de `agents/<nom>/`, mais
  `.claude/settings.json` **ne l'est pas** : seul celui du dossier de lancement
  s'exécute. Celui de la racine devient **inerte** — d'où sa suppression, et
  d'où les hooks appelés en `../../.claude/hooks/…`, en un seul exemplaire ;
- `CLAUDE_PROJECT_DIR` vaut le dossier de **l'agent**, pas la racine du projet ;
- une règle `deny` mord si son chemin est **ancré sur le home**
  (`Edit(~/Agentic/projet/agents/autre/**)`), pas s'il est relatif — et seules
  les règles `Edit(...)` sont évaluées, `Write(...)` est inerte.

---

## Quickstart

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

L'agent scanne le projet, pose les questions nécessaires — **la première étant
« un agent, ou plusieurs ? »**, parce qu'elle décide de l'emplacement du
`.mind/` — puis configure :

- `CLAUDE.md` — le rôle et les règles, adaptés au type de projet détecté
- `.fact/` — les quatre fichiers de faits du projet, plus `roles.md` en multi-agents
- `.mind/` — les deux fichiers d'état de l'agent
- `docs/` — les traces datées
- optionnellement, un site de documentation Quarto (`/publish-docs`)

**4. Coder.** La mémoire se tient toute seule : `mind-guard` refuse un commit
qui laisserait `.mind/` en arrière, et `journal` écrit `.logs/<jour>.md`.

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

`agentic-upgrade` copie ensuite le reste (`.mind/`, `docs/`,
`.mcp.json.example`), migre la mémoire d'une ancienne taxonomie le cas échéant,
et signale tout conflit sans rien écraser.

> Projet **déjà** au harnais, à remettre au niveau de la dernière version →
> `/agentic-sync`.

---

## Ce qui est inclus

### Le harnais

- `CLAUDE.md` — le contexte projet, chargé à chaque session
- `.claude/settings.json` — permissions et câblage des hooks. **En multi-agents,
  celui de la racine n'existe pas** : il ne s'exécuterait pas, et chaque agent
  porte le sien
- `.claude/settings.agent.json.example` — le gabarit d'un agent : hooks appelés
  en `../../`, périmètre en `deny`
- `.claude/settings.local.json.example` — ajustements locaux, non commités
- `.claude/skills/` — les skills disponibles
- `agents/<nom>/` — en multi-agents seulement : trois éléments par agent

### Skills

- `agentic-init` — monte l'**atelier** sur une machine neuve : le socle de méthode
  et le poste du CTO. Une fois par machine, avant tout projet.
- `project-init` — initialise un **nouveau** projet
- `agentic-upgrade` — onboarde un projet existant **sans** harnais (additif)
- `agentic-sync` — resynchronise un projet déjà au harnais. Porte aussi
  `scripts/migre-fact-docs.py`, qui fait passer un projet de l'ancienne
  taxonomie (`.mind/` à cinq fichiers, `.memory/`) à la forme actuelle
- `agentic-agents` — **convertit** un projet mono en multi, ou lui **ajoute** un
  agent. Déplace l'état existant dans `agents/<nom>/`, repointe les hooks en
  `../../`, pose les périmètres en `deny` — et **migre la mémoire auto**, qui
  est classée par chemin : sans ça l'agent repart sur une adresse vide et
  `--resume` ne retrouve rien. Ne découpe pas le `CLAUDE.md` : c'est éditorial
- `agentic-team` — **lit** l'état de tous les projets d'un atelier et en rend deux
  vues : un diagnostic en terminal (« que faut-il lancer sur ce projet ? ») et
  la page **agentic-team**, un fichier HTML autonome qui s'ouvre d'un
  double-clic, sans serveur. Strictement en lecture.
- `agentic-clean` — fait le **ménage** : supprime les caches régénérables
  (`node_modules`, `.next`, `.turbo`, `.venv`, `dist`…) en écrivant en face de
  chacun la commande qui le reconstruit, et **signale sans y toucher** les
  résidus de migration mémoire et les fichiers de `docs/` devenus trop gros.
  Dry-run par défaut. Le ménage n'avait aucun propriétaire avant lui — c'est
  pour cela qu'il n'avait jamais lieu.
- `publish-docs` — génère un site Quarto (HTML + Word/PDF) depuis la mémoire
- `caveman` — mode ultra-compressé, pour réduire les jetons. **Jamais sur
  `.mind/todo.md` ni sur les `.logs/`** : ces fichiers sont relus par un
  programme, et la compression fusionne les listes — `!haut` et `@<qui>`
  disparaîtraient sans erreur.

### Hooks (`.claude/hooks/`)

**`briefing`** — `SessionStart` + `UserPromptSubmit`. Injecte à l'ouverture ce
qui ne tient pas dans un pointeur : le `cap:` (lu dans `.fact/base.md`), la
fraîcheur de la déclaration, les décisions en attente, les **titres de section**
de `base.md`, `stack.md`, `rules.md`, `architecture.md` (plus `roles.md` en
multi-agents), et les règles `deny`
réellement appliquées. Il ne recopie rien — il relit les fichiers à chaque
déclenchement, donc rien ne peut s'y périmer.

Il fait **deux remontées indépendantes** : le `.mind/` le plus proche est l'état
de l'agent qui parle, le `.fact/` le plus proche est son projet. En mono c'est
le même dossier ; en multi, l'agent vit dans `agents/<nom>/` et le `.fact/` est
deux étages plus haut. C'est la raison pour laquelle les deux dossiers ne
portent pas le même nom : une remontée s'arrête au **premier** dossier trouvé,
et deux étages homonymes empêcheraient l'agent de voir jamais l'architecture de
son projet.

**Le seul cas où il parle sans état** : un `.fact/` trouvé *sans* `.mind/`
signifie qu'on est à la racine d'un projet multi-agents, là où personne ne
travaille — l'erreur la plus probable de cette forme. Il avertit et nomme les
agents disponibles, au lieu de se taire : le silence y produirait exactement la
sortie d'un projet en bonne santé.

Sur `UserPromptSubmit` il est **silencieux** tant que rien n'a bougé — coût nul
en régime établi, et il peut donc se poser sur une session **déjà ouverte**.
*Pourquoi un pointeur dans `CLAUDE.md` ne suffisait pas, et la mesure qui l'a
montré : voir le socle, « Les trois hooks ».*

**`mind-guard`** — `PreToolUse` sur `git commit`. Refuse un commit de **code
projet** qui laisserait `state.md` ou `todo.md` en arrière, et refuse un commit
qui les rendrait **illisibles**. L'en-tête qu'il exige : `maj`, `sante`,
`jalon` — le `cap:` a quitté `state.md` pour `.fact/base.md`, parce qu'un projet
n'a qu'une destination même à plusieurs agents.

**Il connaît le lot.** `git diff --cached` renvoie des chemins relatifs à la
racine du dépôt : un agent de `agents/ios/` voit `agents/ios/.mind/state.md`.
Le hook dérive donc son préfixe de `CLAUDE_PROJECT_DIR`. Sans ça il ne garderait
**plus rien** en multi-agents, et sans le dire.

**Il garde `.fact/`.** Ces fichiers sont partagés par tous les agents du projet
et ne s'écrivent qu'à la demande de l'humain : un commit qui y touche est refusé
sans ` # fact-ok` en fin de commande. L'autorisation reste alors dans
l'historique. C'est ce qui rend la règle vérifiable au lieu d'être une consigne.

Trois choses le distinguent de l'ancien `memory-guard` :

1. **Il garde au `commit`, pas au `push`.** Le tableau de bord lit les fichiers
   `.mind/` **sur le disque local**, jamais le dépôt distant : garder au push ne
   protégeait pas ce qu'on croyait protéger.
2. **Il ne suffit plus de « toucher » la mémoire.** Un commit qui ne modifiait
   que `decisions.md` satisfaisait l'ancien hook en laissant `state.md` périmé.
3. **Il vérifie que les fichiers restent lisibles.** C'est le cas le plus grave :
   un en-tête cassé fait sortir le projet du tableau de bord **sans bruit**.

Fail-open sur toute erreur ; échappatoire ` # mind-ok` en fin de commande.
Dormant tant que `git commit` est interdit par défaut (`settings.json`), actif
dès qu'un projet autorise git.

`mind-guard-relais.py` est destiné aux dépôts **multi-domaines** : chaque
sous-périmètre le pose à la place du hook, et il remonte à la racine par
`git rev-parse` — sans compter les dossiers, donc sans casser à la première
réorganisation.

**`journal`** — `PostToolUse` sur `git commit`. Après chaque commit, ajoute au
fichier du jour l'empreinte, le sujet, la branche et les fichiers touchés. Il ne
lit pas le résultat de la commande : il regarde `HEAD`, donc un commit échoué
n'écrit rien et un double appel ne crée pas deux entrées. Silencieux et
fail-open — un journal ne doit jamais empêcher de travailler.

> La règle « tenir la mémoire à jour » n'est plus seulement *énoncée* dans
> `CLAUDE.md`, ni confiée à un skill qu'il fallait penser à lancer : elle est
> **appliquée**. Un journal tenu quand on y pense a des trous exactement les
> jours chargés — ceux qu'on aurait le plus besoin de relire.

### Mémoire — trois dossiers, trois natures

Ce qui les sépare n'est pas le sujet, c'est **le nombre d'écrivains**.

**`.fact/`** — les **faits du projet**, en **quatre fichiers**, plus
`roles.md` en multi-agents. Un
seul écrivain pour tout le projet ; les agents n'y touchent qu'à la demande de
Le commanditaire. Le texte périmé s'y **remplace**, il ne s'ajoute pas.

- `.fact/base.md` — en-tête `cap`, la nature du projet et où il va _(public)_
- `.fact/architecture.md` — domaine, frontières, couches, flux, pièges _(public)_
- `.fact/stack.md` — outils, stack, environnements _(public)_
- `.fact/rules.md` — règles métier, accès, contraintes _(public)_

**`.mind/`** — l'**état d'un agent**, en deux fichiers. Un jeu par agent : à la
racine en mono-agent, dans `agents/<nom>/` quand le projet en porte plusieurs.

- `.mind/state.md` — en-tête `maj / sante / jalon`, phase, ce qui tient, ce qui
  ne tient pas _(public)_
- `.mind/todo.md` — kanban `[ ]` / `[>]` / `[x]`, `!haut`/`!moyen`/`!bas`,
  `@<qui>` _(public)_

**`docs/`** garde les **traces datées** et la matière du domaine, et s'accumule
sans plafond. C'est le seul des trois qui n'est pas caché : **ce qui est caché
est du harnais, ce qui est visible est pour le commanditaire.**

- `docs/README.md` — l'index des trois dossiers
- `docs/decisions.md` — le journal des décisions, *append-only* _(public curé)_
- `docs/operations.md` — 🔒 hébergement, déploiement, secrets, dépannage
  _(**privé — jamais publié, jamais cité, jamais résumé**)_
- `docs/data-model.md` — modélisation détaillée _(conditionnel : data-lourd)_

**Le test qui tranche** : une phrase qui commence par « on a décidé de », ou qui
porte une date au passé, va dans `docs/`. Tout le reste va dans `.mind/`.

**Jamais un sixième fichier dans `.mind/` sans une décision explicite de
l'humain.** Si un contenu n'y rentre pas, c'est qu'il appartient à `docs/`.

**Journal de bord** : le hook `journal` écrit `.logs/<AAAA-MM-JJ>.md` à chaque
commit — committé, *append-only*, jamais élagué ni compressé. Il répond à une
question que `.mind/state.md` ne sait pas traiter : **qu'a-t-on fait mardi ?**
Un instantané ne raconte pas l'histoire, un historique ne dit pas où on en est.

### Site de documentation (optionnel)

- `site/` — moteur Quarto piloté par `site/site.config.yml`
- `/publish-docs [setup|init|refresh|publish]` — installe les outils
  (Quarto/Graphviz), génère les pages depuis la mémoire **publique**, produit un
  site HTML et des livrables Word/PDF, déploie. **Ne lit jamais**
  `operations.md` ni les `.env*`.

---

## Configuration MCP

```bash
cp .mcp.json.example .mcp.json          # macOS / Linux
```

```powershell
Copy-Item .mcp.json.example .mcp.json   # Windows
```

## Permissions locales

Les permissions partagées sont dans `.claude/settings.json`. Pour des
ajustements locaux non commités :

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

- **Python est une dépendance dure** : les hooks en ont besoin. Le nom de
  l'interpréteur diffère (`python` sur Windows, `python3` sur macOS), c'est
  pourquoi `settings.json` déclare le hook **deux fois**. Celle dont
  l'interpréteur manque échoue au démarrage, sans sortie donc sans décision.
- **Aucun script propre à un OS** : ni PowerShell seul, ni shell POSIX seul. Un
  outil qu'une des deux machines ne peut pas lancer ne signale jamais qu'il est
  mort.

## RTK — réduire les jetons dépensés en sortie de shell

[RTK](https://github.com/rtk-ai/rtk) est un binaire Rust qui intercepte la
sortie des commandes shell et la compresse avant qu'elle n'atteigne le contexte
de l'agent : annoncé à **60-90 %** de moins sur les commandes de développement
courantes. Il couvre une centaine de commandes — `git`, `ls`, `grep`, `find`,
`docker`, `kubectl`, `pytest`, `cargo`, `gh`…

**Le binaire ne fait pas partie du starter, et c'est délibéré.** Il s'installe
sur la **machine**, une fois pour toutes les sessions ; le starter pose
l'architecture d'un **projet**. Le vendre avec le dépôt reviendrait à y remettre
une pièce d'exploitation de poste.

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

### Ce que RTK change pour les deux hooks — à lire avant de l'installer

RTK réécrit `git commit` en `rtk git commit`, et son hook renvoie un
`permissionDecision: "allow"` accompagné du `updatedInput`. Les deux hooks du
starter se déclenchent précisément sur `git commit`. D'où deux points de
contact, traités dans `settings.json` :

1. **Les déclencheurs** — `mind-guard` et `journal` sont déclarés sur
   `Bash(git commit*)` **et** sur `Bash(rtk git commit*)`. Sans quoi un hook
   parfaitement sain cesserait de se déclencher le jour où quelqu'un installe
   RTK, sans rien dire. C'est le mode de panne qu'on vient de corriger sur
   `memory-guard` — on ne le réintroduit pas par la porte de derrière.
2. **Le verrou git** — la liste `deny` couvre aussi `rtk git commit*` et
   `rtk git push*`, sinon la réécriture suffisait à le contourner.

**Ce qui n'est pas mesuré, et qu'il faut mesurer une fois.** L'ordre entre le
hook global de RTK et les hooks du projet n'a pas été vérifié : si RTK réécrit
la commande **avant** que `mind-guard` ne la voie, c'est le déclencheur
`rtk git commit*` qui joue ; sinon c'est l'autre. Les deux sont posés, donc le
cas est couvert dans les deux sens — mais **le seul contrôle qui vaut est un
commit d'essai** : tenter un commit de code sans toucher à `.mind/`, et vérifier
que `mind-guard` refuse toujours et que `.logs/<jour>.md` s'écrit toujours. Un
hook qu'on n'a pas vu se déclencher n'est pas un hook vérifié.

## Contribuer

Tout passe par des **skills**, dans `.claude/skills/`. Garde la mémoire dans
`.mind/` et `docs/`, à la racine du projet : elle appartient au projet, pas
au harnais.
