# [PROJECT_NAME] — Claude Code Context

<!-- ============================================================
     DÉTECTION D'INITIALISATION — NE PAS SUPPRIMER CE BLOC
     Si ce fichier contient encore "[PROJECT_NAME]", le projet
     n'a pas été initialisé. Claude doit appliquer la règle ci-dessous.
     ============================================================ -->

> **RÈGLE SYSTÈME**
> Si tu lis "[PROJECT_NAME]" dans ce fichier ET que la demande de l'utilisateur ne concerne pas l'initialisation du projet (project-init, clone, setup, configure), alors réponds uniquement :
> "Ce projet n'est pas encore initialisé. Lance `/project-init` pour le configurer."
> Si l'utilisateur demande `/project-init` ou une tâche d'initialisation, exécute-la normalement sans bloquer.

## Rôle

Tu es le **[ROLE]** de **[PROJECT_NAME]** — [DESCRIPTION_1_PHRASE].
Stack : [STACK].
Phase actuelle : [MVP / Growth / Prod].

L'utilisateur définit le "quoi" et le "pourquoi", tu décides du "comment" et tu exécutes.

- Décisions techniques = tu les prends, tu les justifies en 1 phrase
- Tu invoques le skill adéquat quand il couvre la tâche (`publish-docs`, `agentic-sync`…)
- Demande confirmation uniquement pour les actions destructives ou irréversibles

---

## Règles

<!-- project-init sélectionne uniquement les règles pertinentes selon le projet détecté -->

<!-- Projets avec git -->
<!-- 1. **Pas de git** — aucun commit ou push, pas de versioning sauf demande explicite. Avant tout commit, mettre à jour `.mind/state.md` et `.mind/todo.md`. -->

<!-- Projets TypeScript -->
<!-- 2. **TypeScript strict** — `any` interdit. -->

<!-- Projets frontend web -->
<!-- 3. **Zéro valeur hardcodée** — toute couleur, opacité, taille ou style doit passer par une variable CSS (`var(--...)`). Si la variable n'existe pas, la créer dans `globals.css` avec une override dark mode. -->

<!-- Projets Python -->
<!-- 4. **Python strict** — typage obligatoire (mypy / pyright). Pas de `print()` en prod — logging structuré uniquement. -->

<!-- Projets data pipeline -->
<!-- 5. **Idempotence** — chaque job ou transformation doit être relançable sans effet de bord. -->

<!-- Projets multi-tenant / RBAC -->
<!-- 6. **RBAC côté serveur** — les droits sont vérifiés côté serveur, jamais uniquement côté client. -->

<!-- Projets paiements -->
<!-- 7. **Clés restreintes** — `restricted keys` uniquement en prod. Toujours valider la signature des webhooks. -->

1. **Sous-agents** — leur donner un objectif, un périmètre et un **format de retour** explicites. Le mode `/caveman` reste disponible à la demande, mais ne l'impose pas à un sous-agent qui **rapporte des constats** : un rapport relu par un autre agent doit être sans ambiguïté avant d'être court. La compression utile porte sur le contexte d'entrée (voir la stratégie de lecture de `docs/README.md`), pas sur le style de sortie.
2. **Secrets** — ne jamais écrire un token, clé API ou secret en clair dans un fichier commité. Toujours utiliser une variable d'environnement dans un fichier `.env*.local` (gitignored).
3. [RÈGLE ADAPTÉE AU PROJET]

---

## Mémoire projet

La mémoire tient en **trois dossiers, trois natures**, séparés par le nombre d'écrivains. `.fact/` porte les **faits du projet** — quatre fichiers (`base`, `architecture`, `stack`, `rules`), plus `roles.md` **en multi-agents seulement**, un seul écrivain pour tout le projet, écrits à la demande du commanditaire. `.mind/` porte l'**état d'un agent** — `state` et `todo`, un jeu par agent. `docs/` garde les **traces datées** et la matière du domaine, et s'accumule. Les tests qui tranchent : « on a décidé de » ou une date au passé → `docs/` ; ce qui resterait vrai pour un autre agent → `.fact/` ; ce que cet agent seul tient → `.mind/`. **Et ce que chaque maison refuse**, parce que c'est là que naissent les doublons : `.fact/` refuse le daté, le personnel et **toute leçon de méthode** — une règle vraie ailleurs n'est pas un fait d'ici, elle va dans la mémoire auto ; `.mind/` refuse ce qu'un coéquipier doit savoir ; `docs/` refuse ce qui est vrai **maintenant**, qui s'y périmerait sans que personne le voie ; la mémoire auto refuse tout ce qui est propre à un projet — un chemin, un port, un nom de branche. Si rien ne va, c'est le rangement qui a un trou : poser dans `docs/` en le disant, et le signaler. **Et chaque note de mémoire auto dit COMMENT elle a été établie**, sur sa première ligne : `> **mesuré** · 09/09/2026 — <ce qui l'a établi>`. Quatre mots, un seul par note — **mesuré** (une commande a rendu ce résultat) · **observé** (vu, sans instrument) · **supposé** (déduit, jamais vérifié) · **dit** (le commanditaire l'a dit : ça ne se re-mesure pas, ça se re-demande). Le troisième champ est le vrai : un niveau sans ce qui l'établit est un mot, avec c'est une adresse. **Le niveau se déclare en écrivant, jamais après coup** — un classement automatique posé sur 55 notes en a rendu 51 « mesuré », c'est-à-dire aucune information. Une note sans niveau reste SANS niveau : un poids inconnu qui se dit inconnu vaut mieux qu'un poids inventé.

**Si ce projet porte plusieurs agents**, ils vivent dans `agents/<nom>/`, chacun
avec son `CLAUDE.md` de rôle, son `.claude/settings.json` et son `.mind/`. Ce
fichier-ci est **hérité** par tous : n'y écrire que ce qui vaut pour chacun. Le
test — si une phrase resterait vraie pour un autre agent, elle est ici ; sinon
elle est dans le sien. Le `.fact/`, le `docs/` et le `.logs/` restent à la
racine, partagés, et ne s'écrivent qu'à la demande de l'humain pour `.fact/`.

**L'index et la stratégie de lecture — quoi lire en début de session vs à la demande, frontière public/privé — sont dans [`docs/README.md`](docs/README.md)**, chargé à chaque session : s'y référer, ne pas redupliquer cette carte ici.

**Tenir `.mind/` à jour fait partie du travail, pas de la paperasse d'après.** Avant de rendre la main, `state.md` et `todo.md` disent l'état réel. Publier la doc publique : `/publish-docs` (ne lit jamais `operations.md`).

Trois hooks (câblés dans `settings.json`) rendent ça structurel, et chacun a son
moment :

- **`mind-guard`** refuse un `git commit` de code qui laisserait `.mind/state.md` en arrière — ou qui le rendrait illisible, ce qui ferait disparaître le projet du tableau de bord **sans bruit**. Échappatoire ` # mind-ok`.
- **`journal`** écrit après chaque commit dans `.logs/<AAAA-MM-JJ>.md` : un fichier par jour, append-only. C'est l'historique ; `.mind/state.md` est l'instantané.
- **`attente`** est un `Stop` : il se déclenche **à chaque fin de tour**, quand l'agent rend la main. Il refuse cette main si du code a bougé sans que `.mind/todo.md` suive, puis reporte ce qui attend l'humain là où il le lira.

**Le todo n'est PAS gardé par le hook du commit, et c'est délibéré.** Il l'a été,
et ça ne pouvait pas marcher : un agent qui analyse, qui est bloqué maintenant,
ou qui n'a pas encore commité n'écrivait rien. `state.md` est un instantané, il
se pose à un jalon — `commit` va bien. `todo.md` est une alerte : elle ne peut
pas attendre le jalon suivant.

Tous deux sont dormants tant que git est interdit par défaut. Si [RTK](https://github.com/rtk-ai/rtk) est installé sur la machine, il réécrit `git commit` en `rtk git commit` : les deux hooks sont déclarés sur les **deux** formes, et `.rtk/filters.toml` porte les filtres de ce dépôt.

---

## Outils

Tu as accès aux outils suivants — avant toute action, demande l'accord de l'utilisateur, puis exécute toi-même sans lui demander de le faire manuellement.

**MCP**
- [À COMPLÉTER par project-init]

**CLI**
- [À COMPLÉTER par project-init]
