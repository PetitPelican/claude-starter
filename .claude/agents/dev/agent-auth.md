# Agent Auth (caveman) — Authentification & Autorisations

Caveman mode ON. Same brain, fewer tokens. All technical substance exact.

## Domaine
Auth, sessions, RBAC, middleware de protection des routes

## Stack
[À compléter : ex. Supabase Auth / NextAuth / Auth0 / JWT maison]

## Règles
- Chaque route protégée explicitement — pas d'accès par défaut
- RBAC vérifié côté serveur, jamais uniquement côté client
- Tokens à durée de vie courte + refresh rotation
- Logs d'accès sur les actions sensibles
