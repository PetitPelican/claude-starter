# Session A3/3 — Audit comportemental : Ops & prod

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **1 catégorie sur 5** — la plus dense en points de contrôle. Lance-la dans une nouvelle session Claude Code, indépendamment de A1 et A2.

Fichier de sortie à générer : `AUDIT_COMPORTEMENTAL_A3.md`

---

## Catégorie 5 — Ops & prod

### Risque 19 — Variables d'environnement manquantes ou non validées

Vérifie la gestion des variables d'environnement dans les apps.

Points à vérifier :
- Existe-t-il un fichier `.env.example` à jour listant toutes les variables requises ?
- Les variables sont-elles validées au démarrage de l'app (ex : avec `zod` sur `process.env`) ? Si une variable manque, l'app doit crasher au boot, pas à l'exécution.
- Cherche les usages de `process.env.MA_VARIABLE` dans le code et vérifie que chaque variable est dans `.env.example`.
- Les variables d'environnement publiques (préfixées `NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_` selon le framework) sont-elles uniquement des valeurs non secrètes ?

### Risque 20 — Migrations DB non rejouables en prod

Examine le dossier des migrations.

Vérifie :
- Les migrations sont-elles uniquement dans des fichiers versionnés ? Ou y a-t-il des modifications faites directement dans l'interface d'administration de la DB ?
- Chaque migration est-elle idempotente (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`) ?
- Les migrations utilisent-elles `DROP TABLE` ou `DROP COLUMN` sans garde-fou ?
- L'ordre des migrations est-il cohérent ?
- Existe-t-il une procédure documentée pour rejouer les migrations sur un environnement vierge ?

### Risque 21 — Webhook du provider de paiements sans vérification de signature

Si le projet intègre un provider de paiements (Stripe, Paddle, etc.), examine le handler de webhook.

Vérifie :
- L'événement est-il construit avec une vérification de signature cryptographique ?
- Le body est-il lu en tant que raw bytes (pas parsé en JSON avant la vérification) ?
- La clé secrète du webhook vient-elle bien de `process.env` ?
- Tous les types d'événements reçus sont-ils explicitement gérés ?

Pattern dangereux à détecter :
```typescript
// Problématique — pas de vérification de signature
const body = await req.json()
if (body.type === 'payment.completed') { ... }
```

### Risque 22 — Absence de rate limiting sur les routes publiques

Examine les routes API accessibles sans authentification.

Vérifie :
- Les routes d'inscription ont-elles un rate limiting ?
- Les routes de soumission de données ont-elles une protection contre le spam ?
- Y a-t-il un middleware de rate limiting global ?
- Les fonctions serverless ont-elles leurs propres limites configurées ?

### Risque 23 — Console.log avec données sensibles

Cherche tous les `console.log`, `console.warn`, `console.error`, `console.debug` dans le code source hors tests.

Pour chaque occurrence, évalue si elle contient :
- Des données utilisateur (email, nom, id)
- Des tokens ou sessions (`session`, `token`, `jwt`, `access_token`)
- Des données métier sensibles (abonnements, paiements)

Les occurrences avec données sensibles sont **Critiques**. Les autres sont **Moyennes**.

---

## Format du rapport — AUDIT_COMPORTEMENTAL_A3.md

```markdown
# Audit comportemental — Session A3/3 : Ops & prod
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X

---

## Catégorie 5 — Ops & prod

### Risque 19 — Variables d'environnement
| Variable | Dans .env.example ? | Validée au boot ? | Problème |
|----------|--------------------|--------------------|----------|

### Risque 20 — Migrations DB
| Migration | Idempotente ? | Problème détecté |
|-----------|--------------|-----------------|

### Risque 21 — Webhook paiements
| Point de contrôle | Statut | Détail |
|------------------|--------|--------|

### Risque 22 — Rate limiting
| Route | Protégée ? | Mécanisme |
|-------|-----------|-----------|

### Risque 23 — Console.log sensibles
| Sévérité | Fichier | Ligne | Données exposées |
|----------|---------|-------|-----------------|
```
