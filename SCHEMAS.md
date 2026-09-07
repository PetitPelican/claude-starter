# La méthode en sept schémas

> **Ce document ne fait pas autorité.** La méthode est écrite dans
> [`templates/foundation-CLAUDE.md`](.claude/skills/agentic-init/templates/foundation-CLAUDE.md),
> le fichier que les agents lisent réellement à chaque session. Ici, aucune
> règle nouvelle : seulement **la forme** — l'ordre des phases, ce qui hérite de
> quoi, ce qui bloque quand. La carte, pas le territoire.
>
> **Sept phases, un schéma chacune.** Tout se comprend en ne regardant que les
> schémas.

Conventions : `<racine>/` est le dossier de l'atelier (`~/Agentic`,
`C:\Users\<toi>\Documents\AGENTIC`…), `<projet>/` un projet, et *le
commanditaire* la personne pour qui les agents travaillent.

---

# Phase 1 · Installer l'atelier

```
                        UNE FOIS PAR MACHINE, avant tout projet
                                      │
                              /agentic-init
                                      │
        ┌─────────────────────────────┴─────────────────────────────┐
        │                                                           │
   <racine>/CLAUDE.md                                        <racine>/<cto>/
   ══════════════════                                        ════════════════
   LA MÉTHODE                                                LE POSTE DU PILOTE
   héritée par TOUT sous-dossier                                   │
                                                     ┌─────────────┼─────────────┐
   • la mémoire et ses plafonds                      │             │             │
   • les hooks et ce qu'ils bloquent            CLAUDE.md      .claude/     .fact/ .mind/
   • les frontières entre agents                son RÔLE       hooks        sa mémoire :
   • ce qui attend le commanditaire             seulement      skills       l'atelier,
   • la délégation                              (la méthode,   settings     pas les projets
                                                 il l'hérite)
   ✅ C'EST L'ARTEFACT PORTABLE                                    │
      celui qu'on emmène sur une                            .git/ requis :
      autre machine                                         sans dépôt, 2 hooks
                                                            sur 5 sont inertes

   ┌────────────────────────────────────────────────────────────────────────┐
   │ TROIS NIVEAUX, ET UN SEUL VOYAGE                                       │
   │                                                                        │
   │   ~/.claude/CLAUDE.md ..... LE POSTE     machine, comptes, RAM         │
   │                                          ❌ refait à chaque machine    │
   │   <racine>/CLAUDE.md ...... LA MÉTHODE   mémoire, hooks, frontières    │
   │                                          ✅ portable                   │
   │   <projet>/CLAUDE.md ...... LE PROJET    rôle, stack, règles métier    │
   │                                          ❌ propre au projet           │
   │                                                                        │
   │ ⚠️ PIÈGE : écrire la méthode dans ~/.claude/CLAUDE.md « puisque tout   │
   │    le monde la lit ». Elle y fonctionne — et ne part pas avec le       │
   │    dépôt. Monter le même atelier ailleurs demande alors de trier à la  │
   │    main ce qui est machine et ce qui est méthode.                      │
   └────────────────────────────────────────────────────────────────────────┘
```

---

# Phase 2 · Monter un projet

```
                        ┌──────────────────────────┐
                        │  Qu'est-ce que tu as ?   │
                        └────────────┬─────────────┘
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
         DOSSIER VIDE        DU CODE, PAS         DÉJÀ AU HARNAIS
                 │           DE HARNAIS           (a .claude/skills/,
                 │                   │             .mind/ ou docs/)
    git clone claude-starter .   copier .claude/           │
                 │             depuis le starter           │
                 ▼                   ▼                     ▼
        ╔════════════════╗   ╔════════════════╗   ╔════════════════╗
        ║ /project-init  ║   ║/agentic-upgrade║   ║ /agentic-sync  ║
        ╠════════════════╣   ╠════════════════╣   ╠════════════════╣
        ║ 7 questions    ║   ║ ADDITIF PUR    ║   ║ met à jour le  ║
        ║ Q0 EN PREMIER  ║   ║ copy-if-missing║   ║ starter-owned  ║
        ║ = mono/multi   ║   ║ jamais         ║   ║ (hooks, corps  ║
        ║                ║   ║ d'écrasement   ║   ║  des skills)   ║
        ║ pose tout :    ║   ║ aucune         ║   ║                ║
        ║ CLAUDE.md      ║   ║ suppression    ║   ║ SUPPRIME ce que║
        ║ .fact/ .mind/  ║   ║                ║   ║ le starter a   ║
        ║ docs/ .logs/   ║   ║ remonte        ║   ║ supprimé       ║
        ║ hooks + skills ║   ║ l'ancien       ║   ║                ║
        ║                ║   ║ .claude/memory/║   ║ le project-    ║
        ║                ║   ║ vers docs/     ║   ║ owned : à la   ║
        ║                ║   ║                ║   ║ main           ║
        ╚═══════╤════════╝   ╚═══════╤════════╝   ╚═══════╤════════╝
                └────────────────────┴────────────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │  MONO ou MULTI ?              │
                     │  Deux lots ont-ils des        │
                     │  RYTHMES différents ET des    │
                     │  CONTEXTES disjoints ?        │
                     └───────┬───────────────┬───────┘
                            NON             OUI
                     (la plupart du         │
                      temps)                │
                             ▼               ▼
        ┌────────────────────────┐   ┌────────────────────────┐
        │  MONO                  │   │  MULTI                 │
        │  <projet>/             │   │  <projet>/             │
        │    CLAUDE.md  méthode  │   │    CLAUDE.md  le commun│
        │    .fact/  .mind/      │   │    .fact/ (+roles.md)  │
        │    docs/  .logs/       │   │    docs/  .logs/       │
        │    .claude/  hooks     │   │    .claude/hooks/      │
        │    src/                │   │       source UNIQUE    │
        │                        │   │    src/                │
        │  hooks en              │   │    agents/             │
        │  .claude/hooks/        │   │      <ops>/  CLAUDE.md │
        │                        │   │              .claude/  │
        │                        │   │              .mind/    │
        │                        │   │      <po>/    idem     │
        │                        │   │      <audit>/ idem     │
        │                        │   │                        │
        │                        │   │  hooks en ../../       │
        └───────────┬────────────┘   └───────────┬────────────┘
                    │                            │
                    └──── RÉVERSIBLE ────────────┘
                        /agentic-agents
                    (à tout moment, dans les
                     deux sens)

   ⚠️ « LE PROJET EST GROS » N'EST PAS UNE RÉPONSE.
      Le critère est la DÉPENDANCE, jamais la taille ni la couche technique.
      Découper en back/front est presque toujours faux : la moindre
      fonctionnalité traverse les deux, et aucun agent ne peut la finir seul.
      Un projet gros mais d'un seul tenant se tient très bien à un agent.
```

---

# Phase 3 · Découper en agents

```
╔═══════════════════════════════════════════════════════════════════════════╗
║   PRINCIPE QUI GOUVERNE TOUT LE DÉCOUPAGE                                 ║
║                                                                           ║
║        TOUT LE MONDE LIT TOUT.  SEULE L'ÉCRITURE EST DÉCOUPÉE.            ║
║                                                                           ║
║   Aucun deny ne porte sur la lecture. C'est délibéré : un agent qui ne    ║
║   peut pas lire le code des autres ne peut pas mesurer l'impact du sien,  ║
║   et redemanderait en permanence ce qu'il a sous les yeux.                ║
╚═══════════════════════════════════════════════════════════════════════════╝

                        ┌─────────────────┐
                        │   LE PROJET     │
                        └────────┬────────┘
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────┴─────┐          ┌─────┴─────┐          ┌─────┴─────┐
    │    OPS    │          │    PO     │          │   AUDIT   │
    │ le socle  │          │ le produit│          │ l'épreuve │
    └───────────┘          └───────────┘          └───────────┘
   ce sur quoi tout      ce que l'utilisateur    ce qui menace
   repose et qui ne      voit et touche          l'ensemble
   se voit pas

┌───────────────────────────────────────────────────────────────────────────┐
│  OPS — LE SOCLE                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│  LIT      tout le projet                                                  │
│  ÉCRIT    base de données · migrations · sécurité des accès · API ·       │
│           paiements · CI/CD · scripts · configuration du monorepo         │
│  N'ÉCRIT  tout ce que l'utilisateur voit                                  │
│  LIVRE    un système qui tient                                            │
│  RYTHME   lent, irréversible          BRANCHE  la principale de travail   │
├───────────────────────────────────────────────────────────────────────────┤
│  DENY — stratégie LISTE NOIRE, une quinzaine de règles                    │
│     Edit(~/<racine>/<projet>/landing/**)                                  │
│     Edit(~/<racine>/<projet>/maquettes/**)                                │
│     Edit(~/<racine>/<projet>/packages/{produit-1,produit-2,…}/**)         │
│     Edit(~/<racine>/<projet>/apps/web/{hooks,e2e,public,scripts}/**)      │
│     Edit(~/<racine>/<projet>/agents/<po>/**)                              │
│     Edit(~/<racine>/.worktrees/**)                                        │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  PO — LE PRODUIT                                                          │
├───────────────────────────────────────────────────────────────────────────┤
│  LIT      tout le projet                                                  │
│  ÉCRIT    interfaces web et mobile · paquets produit · landing ·          │
│           maquettes · builds                                              │
│  N'ÉCRIT  le socle · la mise en production                                │
│  LIVRE    des fonctionnalités                                             │
│  RYTHME   rapide, itératif            BRANCHE  la sienne (worktree)       │
├───────────────────────────────────────────────────────────────────────────┤
│  DENY — ⚠️ LE PIÈGE À NE PAS REPRODUIRE                                   │
│                                                                           │
│     Edit(~/<racine>/<projet>/**)          ← tout le dépôt principal       │
│     Edit(~/<racine>/.worktrees/<po>/agents/<ops>/**)                      │
│                                                                           │
│  Deux règles suffisent à l'isoler du dépôt principal — et DANS SON        │
│  PROPRE WORKTREE, PLUS RIEN NE L'ARRÊTE. La base de données, la CI,       │
│  l'API, les paquets partagés lui sont ouverts : tout ce que roles.md      │
│  attribue à OPS.                                                          │
│                                                                           │
│  Sa frontière tient alors à sa DISCIPLINE, pas à la machine — et c'est    │
│  précisément ce que les deny existent pour éviter.                        │
│  ► ÉNUMÉRER les dossiers interdits DANS son propre arbre de travail.      │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  AUDIT — L'ÉPREUVE                                                        │
├───────────────────────────────────────────────────────────────────────────┤
│  LIT      tout le projet — le SEUL à qui rien n'est interdit en lecture   │
│           ET tout interdit en écriture                                    │
│  ÉCRIT    RIEN DU CODE. Uniquement docs/audit/<date>/ et son .mind/       │
│  N'ÉCRIT  tout le reste — et il ne RÉPARE JAMAIS ce qu'il constate        │
│  LIVRE    un état des lieux + un plan de remédiation                      │
│  RYTHME   périodique, transversal     BRANCHE  la sienne (worktree)       │
├───────────────────────────────────────────────────────────────────────────┤
│  DENY — la couverture la plus complète : une vingtaine de règles          │
│     Edit(~/<racine>/.worktrees/<audit>/{apps,packages,db,scripts}/**)     │
│     Edit(~/<racine>/.worktrees/<audit>/{landing,maquettes,dist,.github}/**)│
│     Edit(~/<racine>/.worktrees/<audit>/{package.json,tsconfig.json,…})    │
│     Edit(~/<racine>/.worktrees/<audit>/.fact/**)                          │
│     Edit(~/<racine>/.worktrees/<audit>/agents/{<ops>,<po>}/**)            │
│     Edit(~/<racine>/<projet>/**)   Edit(~/<racine>/.worktrees/<po>/**)    │
├───────────────────────────────────────────────────────────────────────────┤
│  SON INDÉPENDANCE VIENT DE SON ABSENCE D'AUTORITÉ.                        │
│  S'il pouvait ordonner, il auditerait ses propres décisions. Comme        │
│  l'audit interne en entreprise : accès à tout, autorité sur rien.         │
│                                                                           │
│  ⚠️ NE PAS LE RENOMMER « chef de projet ». Le nom d'un rôle façonne le    │
│     comportement de l'agent qui le porte : il finirait par donner des     │
│     ordres aux autres, et le seul point de contrôle humain tomberait.     │
└───────────────────────────────────────────────────────────────────────────┘
```

## Comment s'écrit un périmètre — et les trois façons de le rater

```
   LE PÉRIMÈTRE S'ÉCRIT DANS settings.json, EN deny, ET NULLE PART AILLEURS.
   Une consigne en prose dans un CLAUDE.md n'empêche rien : elle est lue,
   comprise, et contournée à la première urgence.

   ✅  "deny": ["Edit(~/<racine>/<projet>/db/**)"]
                     ▲              ▲
                     │              └── ancré sur le HOME
                     └───────────────── Edit, jamais Write

   ❌  "deny": ["Edit(../autre/**)"]      chemin RELATIF → NE MORD PAS
                                          mesuré : le fichier a été modifié
                                          malgré la règle

   ❌  "deny": ["Write(~/<racine>/…/**)"] Write est INERTE
                                          avertissement au démarrage,
                                          que personne ne lit

   ⚠️  UN deny NE COUVRE PAS ce qu'un script écrit via Bash.

   ┌──────────────────────────┬──────────────────────────────────────────┐
   │ LISTE NOIRE              │ LISTE BLANCHE implicite                  │
   │ j'énumère ce que je NE   │ j'interdis le dépôt principal, et je     │
   │ touche pas               │ suis libre chez moi                      │
   ├──────────────────────────┼──────────────────────────────────────────┤
   │ sûre mais verbeuse :     │ FAUSSE SÉCURITÉ : tout dossier non listé │
   │ tout dossier créé plus   │ est ouvert, aujourd'hui comme demain     │
   │ tard est ouvert par      │                                          │
   │ défaut → à relire à      │ ► à n'employer QUE si l'agent n'a         │
   │ chaque nouveau lot       │   réellement aucun voisin dans son arbre │
   └──────────────────────────┴──────────────────────────────────────────┘
```

## L'ordre de mise en place

```
   1 ── CHOISIR LES RÔLES ................ references/roles.md
        (le choix, pas la mécanique — c'est lui qui décide de tout le reste)
                    │
   2 ── /agentic-agents .................. déplace l'état dans agents/<nom>/
        │                                  migre la mémoire auto
        │                                  repointe les hooks en ../../
        │
        └─► ⚠️ la mémoire auto est classée par CHEMIN.
            Sans migration, elle est perdue EN SILENCE.
                    │
   3 ── ÉCRIRE LES deny .................. ancrés sur le home, avec Edit,
        │                                  Y COMPRIS dans son propre arbre
                    │
   4 ── ÉCRIRE .fact/roles.md ............ LE 5e FICHIER, l'étape qu'on oublie
        │                                  • qui tient quoi
        │                                  • LES ZONES PARTAGÉES ← sa raison d'être
        │                                  • les frontières qui ne sont pas
        │                                    des dossiers (branches, CI, worktrees)
        │
        └─► POURQUOI : le rôle d'un agent est écrit dans SON CLAUDE.md,
            que LUI SEUL charge. Chacun connaît sa frontière et ignore
            celle des autres. Constaté : un agent a dû DÉDUIRE le périmètre
            d'un tiers pour ne pas l'enfreindre, et un dossier a été écrit
            par deux mains sans que son propriétaire déclaré le sache.
                    │
   5 ── UN WORKTREE PAR AGENT ............ sinon deux agents partagent un seul
                                           HEAD — les deny n'isolent que des
                                           CHEMINS, pas l'index ni la branche
                    │
        └─► ⚠️ un worktree naît SANS les fichiers ignorés (.env, .mcp.json,
            settings.local.json). type-check, lint et test passent au vert
            sans les voir : le trou n'apparaît qu'au premier build.
```

---

# Phase 4 · Les `CLAUDE.md` — avant de leur parler

> On définit ce que chaque agent sait de lui-même **avant** d'ouvrir la
> première conversation. Un rôle écrit après coup ne rattrape pas les tours
> déjà joués.

```
╔══════════════════════════════════════════════════════════════════════════╗
║  LA RÈGLE, MESURÉE : un agent lit tous les CLAUDE.md AU-DESSUS de lui,   ║
║  jamais ceux d'à côté, jamais ceux d'en dessous — sauf s'il va les       ║
║  chercher.                                                               ║
╚══════════════════════════════════════════════════════════════════════════╝

 NIVEAU 1 ─ LE POSTE ───────────────────────── ~/.claude/CLAUDE.md
 │  la machine : RAM, comptes, sessions,        lu par : TOUS les agents
 │  sous-agents, ce qui ne se délègue pas       de la machine
 │  ❌ NON PORTABLE — refait par machine
 │
 ├─ NIVEAU 2 ─ LA MÉTHODE ──────────────────── <racine>/CLAUDE.md
 │  │  mémoire, hooks, frontières,              lu par : TOUS les agents
 │  │  ce qui attend le commanditaire           de l'atelier
 │  │  ✅ PORTABLE — c'est L'ARTEFACT
 │  │
 │  ├─ NIVEAU 3 ─ LE PROJET ────────────────── <projet>/CLAUDE.md
 │  │  │  rôle, stack, règles métier            lu par : tous les agents
 │  │  │                                        DE CE PROJET
 │  │  │
 │  │  └─ NIVEAU 4 ─ LE RÔLE ───────────────── agents/<nom>/CLAUDE.md
 │  │        son périmètre, son cap             lu par : CET AGENT SEUL
 │  │        ⚠️ les autres l'IGNORENT ──────────► d'où .fact/roles.md
 │  │
 │  └─ <autre projet>/CLAUDE.md   ◄── JAMAIS lu par le projet voisin
 │
 └─ chaque projet est une branche indépendante

┌──────────────┬────────────────────────────┬──────────────────────────────┐
│ NIVEAU       │ CONTIENT                   │ NE DOIT JAMAIS CONTENIR      │
├──────────────┼────────────────────────────┼──────────────────────────────┤
│ 1 · Poste    │ ce qui change le           │ l'inventaire des projets —   │
│              │ comportement sur CETTE     │ ça vieillit et personne ne   │
│              │ machine                    │ le corrige                   │
├──────────────┼────────────────────────────┼──────────────────────────────┤
│ 2 · Méthode  │ l'invariant commun à TOUT  │ un fait vrai d'un seul       │
│              │ projet                     │ projet                       │
├──────────────┼────────────────────────────┼──────────────────────────────┤
│ 3 · Projet   │ le rôle, la stack, les     │ l'avancement — il vit dans   │
│              │ règles métier              │ .mind/state.md ; une copie   │
│              │                            │ se périme en silence         │
├──────────────┼────────────────────────────┼──────────────────────────────┤
│ 4 · Rôle     │ le périmètre de CET agent  │ le périmètre des autres — il │
│              │                            │ ne l'appliquerait pas, et le │
│              │                            │ croirait à jour              │
└──────────────┴────────────────────────────┴──────────────────────────────┘

   EN CAS DE CONFLIT, LE PLUS SPÉCIFIQUE GAGNE.
   Le niveau 2 ne « prévaut » pas sur le 3 : les deux sont lus, et le plus
   proche l'emporte. Écraser depuis le parent produit deux textes qui se
   contredisent — et c'est le plus précis qui gagne de toute façon.

   UN CLAUDE.md PARTAGÉ EST NORMATIF, PAS UN INVENTAIRE.
   « C'est vrai » n'est pas un motif d'inclusion. La seule question :
   est-ce que ça change le comportement d'un agent ? Sinon → .fact/.

╔══════════════════════════════════════════════════════════════════════════╗
║  L'AUTRE HÉRITAGE — CELUI QUI NE SE FAIT PAS                             ║
║  Le piège du multi-agents, une demi-journée pour qui le découvre seul.   ║
║                                                                          ║
║     CLAUDE.md ───────────────► HÉRITÉ par agents/<nom>/         ✅       ║
║     .claude/settings.json ───► PAS HÉRITÉ                       ❌       ║
║                                seul celui du dossier de LANCEMENT       ║
║                                s'exécute. Celui de la racine devient    ║
║                                INERTE.                                   ║
║                                                                          ║
║     d'où ──► les hooks sont appelés en ../../.claude/hooks/,            ║
║              en UN SEUL exemplaire, depuis chaque agent                 ║
║                                                                          ║
║     et  ──► CLAUDE_PROJECT_DIR vaut le dossier de L'AGENT,              ║
║             pas la racine du projet                                     ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

# Phase 5 · Le workflow d'un échange

```
   LE COMMANDITAIRE ÉCRIT UN MESSAGE
   │
   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ ①  AVANT QUE L'AGENT RÉPONDE                                             │
│    événement  SessionStart (au démarrage) · UserPromptSubmit (ensuite)   │
│    hook       briefing.py                                                │
├──────────────────────────────────────────────────────────────────────────┤
│    INJECTE dans son contexte :                                           │
│      • le cap du projet          • le nombre de décisions en attente     │
│      • la fraîcheur de son état  • les droits réellement appliqués       │
│      • les TITRES DE SECTION de chaque fichier de .fact/                 │
│                                                                          │
│    N'INJECTE PAS leur contenu — ce serait la faute que .fact/ existe     │
│    pour éviter : une copie qui se périme en silence.                     │
│                                                                          │
│    Se tait si .mind/ n'a pas changé depuis le tour précédent — coût nul  │
│    en régime établi. Il peut donc se poser sur une session DÉJÀ ouverte. │
│                                                                          │
│    DEUX REMONTÉES INDÉPENDANTES :                                        │
│      le .mind/ le plus proche ─► l'état de l'agent qui parle             │
│      le .fact/ le plus proche ─► son projet                              │
│    En mono c'est le même dossier. En multi, l'agent vit dans             │
│    agents/<nom>/ et le .fact/ est deux étages plus haut.                 │
│                                                                          │
│    ⚠️ LE SEUL CAS OÙ IL PARLE SANS ÉTAT : un .fact/ trouvé SANS .mind/   │
│    signifie qu'on a ouvert la session à la racine d'un projet            │
│    multi-agents — là où personne ne travaille, l'erreur la plus          │
│    probable de cette forme. Il avertit et nomme les agents disponibles,  │
│    au lieu de se taire : le silence y produirait exactement la sortie    │
│    d'un projet en bonne santé.                                           │
│                                                                          │
│    LA PANNE QU'IL CORRIGE : un agent interrogé sur ses propres outils    │
│    a répondu de travers, alors que la réponse tenait dans son            │
│    .fact/stack.md, à jour du jour même. Rien dans son démarrage ne       │
│    NOMMAIT ce fichier.                                                   │
└──────────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ ②  IL TRAVAILLE                                        aucun hook        │
│    il lit, écrit, teste, mesure — rien ne le surveille                   │
└──────────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ ③  IL VEUT ENREGISTRER SON TRAVAIL                                       │
│    événement  PreToolUse (Bash) — le script filtre lui-même sur          │
│               `git commit`                                               │
│    hook       mind-guard.py                                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│        .mind/state.md est-il présent, frais, et PARSE-t-il encore ?      │
│                    │                              │                      │
│                   NON                            OUI                     │
│                    │                              │                      │
│              ┌─────▼─────┐                        │                      │
│              │  REFUSÉ   │                        │                      │
│              │ le commit │                        │                      │
│              │ n'a pas   │                        │                      │
│              │ lieu      │                        │                      │
│              └─────┬─────┘                        │                      │
│                    │                              │                      │
│         il met son état à jour                    │                      │
│                    └──────────────────────────────┤                      │
│                                                   │                      │
│        le commit touche-t-il .fact/ ?             │                      │
│                    │                              │                      │
│                   OUI ── sans ` # fact-ok` ──► REFUSÉ                    │
│                    │      (.fact/ est lu par TOUS les agents :           │
│                    │       un fait faux s'y propage en silence)          │
│                   NON                             │                      │
│                    └──────────────────────────────┤                      │
│                                                   ▼                      │
│    échappatoire ` # mind-ok`                  LE COMMIT PASSE            │
│                                                                          │
│    ⚠️ IL CONNAÎT LE LOT. `git diff --cached` renvoie des chemins         │
│    relatifs à la racine du DÉPÔT : un agent de agents/<nom>/ y voit      │
│    « agents/<nom>/.mind/state.md ». Le hook dérive donc son préfixe de   │
│    CLAUDE_PROJECT_DIR. Sans ça il ne garderait PLUS RIEN en              │
│    multi-agents — et sans le dire.                                       │
│                                                                          │
│    Fail-open sur toute erreur. Dormant tant que `git commit` est         │
│    interdit par défaut, actif dès qu'un projet autorise git.             │
└──────────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ ③bis LE COMMIT VIENT DE PASSER                                           │
│    événement  PostToolUse (Bash) sur `git commit`                        │
│    hook       journal.py                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│    ÉCRIT .logs/<AAAA-MM-JJ>.md en lisant HEAD.                           │
│    Append-only — rien ne s'y réécrit. Un fichier par jour ET par agent.  │
│                                                                          │
│    Ne demande RIEN à l'agent : c'est la machine qui tient le journal.    │
│    Un journal qu'on tient quand on y pense a des trous exactement les    │
│    jours chargés — ceux qu'on aurait le plus besoin de relire.           │
└──────────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ ④  IL A FINI DE PARLER, IL VA RENDRE LA MAIN                             │
│    événement  Stop — « when Claude finishes responding », 1× par tour    │
│    hook       attente.py                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   a.  Du code projet a-t-il bougé sans que .mind/todo.md suive ?         │
│                    │                              │                      │
│                   OUI                            NON                     │
│                    │                              │                      │
│           ┌────────▼────────┐                     │                      │
│           │  IL NE PEUT PAS │                     │                      │
│           │  RENDRE LA MAIN │  garde anti-boucle :│                      │
│           │  il est renvoyé │  on ne bloque qu'UNE│                      │
│           │  au travail     │  fois par état du   │                      │
│           └────────┬────────┘  code. Au pire un   │                      │
│                    │           rappel manqué,     │                      │
│      il note ce qui attend     jamais un agent    │                      │
│      le commanditaire          coincé.            │                      │
│                    └──────────────────────────────┤                      │
│                                                   ▼                      │
│   b.  POUSSE les demandes ouvertes vers LE CANAL DU COMMANDITAIRE        │
│       triées par priorité, avec pastille 🔴 🟠 🟡                        │
│       (canal par défaut : la liste de rappels du système — remplaçable)  │
│                                                   │                      │
│   c.  RELIT ce canal                              ▼                      │
│       ├── une entrée COCHÉE ────────► il a tranché : l'agent est renvoyé │
│       │                               au travail AVEC la décision        │
│       └── une entrée AJOUTÉE ───────► (reconnaissable : pas de pastille, │
│           sans pastille               que seul l'outil pose)             │
│                                       c'est une demande QU'IL adresse    │
│                                       à l'agent                          │
│                                                                          │
│       PURGE uniquement ce qu'un agent a écrit (test de la pastille) —    │
│       jamais les entrées du commanditaire.                               │
│                                                                          │
│   FAIL-OPEN PARTOUT. Un hook de reporting ne doit jamais empêcher de     │
│   travailler : toute erreur, tout doute, tout projet hors harnais        │
│   sort en 0.                                                             │
└──────────────────────────────────────────────────────────────────────────┘
   │
   ▼
   IL REND LA MAIN

╔══════════════════════════════════════════════════════════════════════════╗
║  LES DEUX REFUS — ③ et ④a — SONT TOUT LE SYSTÈME.                        ║
║  Ce ne sont pas des consignes de prose : on a mesuré que la prose ne     ║
║  suffit pas. Ce sont des blocages mécaniques. L'agent ne PEUT PAS        ║
║  passer à la suite.                                                      ║
║                                                                          ║
║  POURQUOI ④ N'EST PAS SUR LE COMMIT : un agent qui analyse, qui est      ║
║  bloqué maintenant, ou qui n'a pas encore commité n'écrivait RIEN.       ║
║  Sur l'atelier de référence, 124 demandes s'étaient accumulées sur       ║
║  10 projets sans qu'aucune ne remonte.                                   ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

# Phase 6 · La boucle de décision

```
   l'agent est bloqué                    le commanditaire tranche
          │                                         ▲
          ▼                                         │
   .mind/todo.md          son canal                 │
   - [ ] !haut @user  ──►  🔴 Autoriser le    ──►  il coche
       **Autoriser…**      paiement en ligne       depuis son
          ▲                                        téléphone
          │                                         │
          └────── l'agent applique et coche ◄───────┘

   ┌──────────────────────────────────────────────────────────────────────┐
   │  TROIS CHOSES PAR DEMANDE, RIEN D'AUTRE                              │
   │                                                                      │
   │    - [ ] !haut @user **Autoriser le paiement en ligne**              │
   │          Sans ça la boutique ne peut pas encaisser ;                 │
   │          toi seul peux signer.                                       │
   │          J'ai continué sur le reste ; ça attend depuis 4 jours.      │
   │                                                                      │
   │    ① ce qu'on lui demande                                            │
   │    ② pourquoi ce ne peut être QUE lui                                │
   │    ③ ce qui se passe s'il ne répond pas                              │
   │                                                                      │
   │  INTERDIT : nom de fichier, de fonction, de variable.                │
   │  « ADMIN_EMAILS, lue par apps/web/lib/admin/guard.ts » ne lui dit    │
   │  rien et lui coûte un aller-retour. Il prend de la hauteur ; le      │
   │  détail technique est le métier de l'agent, pas le sien.             │
   └──────────────────────────────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────────────────┐
   │  L'AGENT NE S'ARRÊTE PAS POUR DEMANDER.                              │
   │  Il prend le chemin réversible, note son hypothèse, continue.        │
   │  Il ne s'arrête QUE si poursuivre serait irréversible ou rendrait    │
   │  le travail faux.                                                    │
   │                                                                      │
   │  ⚠️ UN AGENT NE PEUT PAS EN DÉBLOQUER UN AUTRE. Relayer une          │
   │     autorisation contourne le seul point de contrôle humain de la    │
   │     chaîne. Un agent sollicité par un pair doit refuser — et sur     │
   │     l'atelier de référence, il l'a fait.                             │
   └──────────────────────────────────────────────────────────────────────┘

   LE CANAL SE LIT DANS LES DEUX SENS
     🔴🟠🟡 avec pastille  ──► écrit par un agent, il attend une décision
        sans pastille      ──► écrit par le commanditaire : une demande que
                               l'agent prend au tour suivant, puis coche
                               pour lui répondre
```

---

# Phase 7 · La mémoire

```
~/.claude/projects/<chemin-slugifié>/memory/
│  ═══════════════════════════════════════════ MÉMOIRE AUTO
│  les constats transversaux, ce qui ne rentre    écrit : l'agent seul
│  nulle part ailleurs                            lu    : lui seul
│  ⚠️ CLASSÉE PAR CHEMIN — déplacer le projet
│     la perd EN SILENCE. La déplacer fait
│     partie du renommage.
│
└── LE PROJET
    │
    ├── .fact/ ══════════════════ LES FAITS DU PROJET ══ plafond 4 (+1)
    │   │                          écrit : à la demande du commanditaire
    │   │                                  (` # fact-ok` au commit)
    │   │                          lu    : TOUS les agents du projet
    │   ├── base.md ............ la nature, le cap
    │   ├── architecture.md .... les frontières, l'agencement
    │   ├── stack.md ........... outils, comptes, accès, versions
    │   ├── rules.md ........... ce qu'on ne franchit pas
    │   └── roles.md ........... ⟵ MULTI-AGENTS SEULEMENT
    │                             qui tient quoi · les zones partagées ·
    │                             les frontières qui ne sont pas des dossiers
    │
    ├── .mind/ ══════════════════ L'ÉTAT D'UN AGENT ═══ plafond 2
    │   │                          UN JEU PAR AGENT
    │   │                          écrit : cet agent
    │   │                          lu    : lui + le tableau de bord + le canal
    │   ├── state.md ........... un INSTANTANÉ borné — le périmé s'y REMPLACE
    │   └── todo.md ............ ce qui attend le commanditaire
    │
    ├── docs/ ═══════════════════ LES TRACES DATÉES ═══ aucun plafond
    │   │                          écrit : qui veut
    │   │                          lu    : les humains, surtout
    │   ├── decisions.md ....... le pourquoi de chaque choix, daté
    │   ├── operations.md ...... ⚠️ PRIVÉ — jamais publié (secrets, dépannage)
    │   └── audit/<date>/ ...... les livrables d'Audit
    │
    └── .logs/ ══════════════════ LE JOURNAL AUTOMATIQUE ═ aucun plafond
        └── <jour>.md .......... append-only, un par jour ET par agent
                                  écrit : LA MACHINE, jamais à la main
                                  lu    : le commanditaire, après coup

╔══════════════════════════════════════════════════════════════════════════╗
║  LE TEST QUI RANGE N'IMPORTE QUELLE INFORMATION                          ║
║                                                                          ║
║   « on a décidé de… » ou une date au passé  ──────────►  docs/          ║
║   vrai pour un AUTRE agent du projet        ──────────►  .fact/         ║
║   tenu par CET agent seul                   ──────────►  .mind/         ║
║   écrit par un hook, jamais à la main       ──────────►  .logs/         ║
╚══════════════════════════════════════════════════════════════════════════╝

   POURQUOI DES PLAFONDS ....... sans eux, .mind/ dérive et plus personne ne
                                 le lit. Un fichier de mémoire qu'on ne relit
                                 pas est PIRE qu'absent : il a l'air d'être
                                 à jour.

   DEUX NATURES, JAMAIS MÊLÉES . .mind/ = des faits ACTUELS
                                 docs/  = un HISTORIQUE
                                 Un instantané ne répond pas à « qu'a-t-on
                                 fait mardi ? ». Un historique ne répond pas
                                 à « où en est-on ? ».

   POUR QUI ELLE EST ÉCRITE .... cette mémoire ne sert pas d'abord à l'agent,
                                 elle sert au COMMANDITAIRE — voir où en est
                                 un projet sans ouvrir le dépôt. D'où le ton
                                 de state.md : il s'écrit pour quelqu'un qui
                                 n'a pas lu le code.

   CE QUI EST CACHÉ EST DU HARNAIS, CE QUI EST VISIBLE EST POUR LE
   COMMANDITAIRE. docs/ est le seul des quatre à ne pas commencer par un
   point — et c'est le seul qu'il ouvre lui-même.

╔══════════════════════════════════════════════════════════════════════════╗
║  POURQUOI .fact/ ET .mind/ NE PORTENT PAS LE MÊME NOM                    ║
║                                                                          ║
║  Une remontée de dossier s'arrête au PREMIER trouvé. Un agent qui vit    ║
║  dans agents/<nom>/ remonte deux fois :                                  ║
║                                                                          ║
║     agents/<nom>/.mind/  ◄── trouvé tout de suite : SON état             ║
║     <projet>/.fact/      ◄── deux étages plus haut : SON projet          ║
║                                                                          ║
║  Deux étages HOMONYMES arrêteraient la seconde remontée sur la           ║
║  première — et l'agent ne verrait JAMAIS l'architecture de son projet.   ║
║  Le nom distinct n'est pas cosmétique : c'est ce qui rend les deux       ║
║  remontées indépendantes.                                                ║
╚══════════════════════════════════════════════════════════════════════════╝

   ⚠️ .mind/todo.md ET .logs/ NE PASSENT JAMAIS par une compression de texte
      (/caveman et apparentés) : ses règles fusionnent les listes, et les
      marqueurs de priorité et de destinataire disparaîtraient SANS ERREUR.
      Le tableau de bord afficherait des tâches sans priorité ni destinataire
      — exactement l'information que ces fichiers portent.
```

---

# Les six pièges, en une page

```
 ①  LA MÉTHODE ÉCRITE AU NIVEAU DU POSTE
     Elle fonctionne, et elle ne part pas avec le dépôt. Monter le même
     atelier ailleurs demande alors de trier à la main.
     ► la méthode vit dans <racine>/CLAUDE.md, jamais dans ~/.claude/

 ②  UN PÉRIMÈTRE EN PROSE
     Une consigne dans un CLAUDE.md est lue, comprise, et contournée à la
     première urgence.
     ► le périmètre s'écrit en deny, ancré sur le home, avec Edit

 ③  LA LISTE BLANCHE IMPLICITE
     « J'interdis le dépôt principal, je suis libre chez moi » laisse ouvert
     tout ce qui n'est pas listé — aujourd'hui comme demain.
     ► énumérer les interdits DANS son propre arbre de travail

 ④  LE settings.json QU'ON CROIT HÉRITÉ
     Seul celui du dossier de lancement s'exécute. Celui de la racine est
     INERTE, et rien ne le dit.
     ► hooks appelés en ../../, en un seul exemplaire

 ⑤  LA MÉMOIRE AUTO OUBLIÉE AU DÉMÉNAGEMENT
     Elle est classée par CHEMIN. Renommer ou déplacer un projet la perd
     sans aucun message.
     ► la déplacer fait partie du renommage

 ⑥  LE RÔLE RENOMMÉ EN TITRE HIÉRARCHIQUE
     Le nom d'un rôle façonne le comportement de l'agent qui le porte.
     Un « chef de projet » finira par donner des ordres aux autres, et le
     seul point de contrôle humain tombe.
     ► un agent ne peut jamais en débloquer un autre
```

---

_Les schémas décrivent le harnais livré par ce dépôt. En cas d'écart entre ce
document et
[`templates/foundation-CLAUDE.md`](.claude/skills/agentic-init/templates/foundation-CLAUDE.md),
**c'est le second qui fait foi** — et l'écart est un défaut à corriger ici._
