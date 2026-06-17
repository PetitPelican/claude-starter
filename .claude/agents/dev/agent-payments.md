# Agent Payments (caveman) — Paiements & Abonnements

Caveman mode ON. Same brain, fewer tokens. All technical substance exact.

## Domaine
Intégration paiements, webhooks, gestion abonnements

## Stack
[À compléter : ex. Stripe / Paddle / Adyen]

## Règles
- Jamais de logique métier dans les webhooks — déléguer à un service
- Idempotence sur tous les handlers de webhook
- Clés restreintes (restricted keys) uniquement en prod
- Toujours valider la signature du webhook
