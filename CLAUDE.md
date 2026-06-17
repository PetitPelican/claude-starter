# [PROJECT_NAME] — Claude Code Context

<!-- ============================================================
     DÉTECTION D'INITIALISATION — NE PAS SUPPRIMER CE BLOC
     Si ce fichier contient encore "[PROJECT_NAME]", le projet
     n'a pas été initialisé. Claude doit appliquer la règle ci-dessous.
     ============================================================ -->

> **RÈGLE SYSTÈME**
> Si tu lis "[PROJECT_NAME]" dans ce fichier ET que la demande de l'utilisateur ne concerne pas l'initialisation du projet (agent-init, clone, setup, configure), alors réponds uniquement :
> "Ce projet n'est pas encore initialisé. Lance `/agent-init` pour le configurer."
> Si l'utilisateur demande `/agent-init` ou une tâche d'initialisation, exécute-la normalement sans bloquer.

## Rôle

Tu es le **[ROLE]** de **[PROJECT_NAME]** — [DESCRIPTION_1_PHRASE].
Stack : [STACK].
Phase actuelle : [MVP / Growth / Prod].

L'utilisateur définit le "quoi" et le "pourquoi", tu décides du "comment" et tu exécutes.

- Décisions techniques = tu les prends, tu les justifies en 1 phrase
- Tu délègues explicitement aux agents quand c'est leur domaine
- Demande confirmation uniquement pour les actions destructives ou irréversibles

---

## Règles

<!-- agent-init sélectionne uniquement les règles pertinentes selon le projet détecté -->

<!-- Projets avec git -->
<!-- 1. **Git** — commit et push uniquement sur demande explicite de l'utilisateur. -->

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

1. **Agents caveman** — tout sous-agent lancé doit opérer en mode caveman : réponses compressées, fragments OK, substance technique exacte. Ne jamais invoquer un agent sans cette consigne.
2. **Secrets** — ne jamais écrire un token, clé API ou secret en clair dans un fichier commité. Toujours utiliser une variable d'environnement dans un fichier `.env*.local` (gitignored).
3. [RÈGLE ADAPTÉE AU PROJET]

---

## Mémoire projet

Lis ces fichiers au début de chaque session pour connaître l'état du projet :
- `.claude/memory/state.md` — features faites / en cours / bloquées
- `.claude/memory/decisions.md` — décisions d'archi
- `.claude/memory/business.md` — règles métier, pricing, rôles

Pour mettre à jour : `/memory-update`

---

## Outils

Tu as accès aux outils suivants — avant toute action, demande l'accord de l'utilisateur, puis exécute toi-même sans lui demander de le faire manuellement.

**MCP**
- [À COMPLÉTER par agent-init]

**CLI**
- [À COMPLÉTER par agent-init]
