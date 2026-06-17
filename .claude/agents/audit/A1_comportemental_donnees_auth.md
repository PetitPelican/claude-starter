# Session A1/3 — Audit comportemental : Données & DB + Auth & accès

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **2 catégories sur 5**. Les sessions A2 et A3 couvriront les suivantes dans des sessions séparées. Ne traite pas les catégories des autres sessions.

Fichier de sortie à générer : `AUDIT_COMPORTEMENTAL_A1.md`

---

## Catégorie 1 — Données & DB

### Risque 1 — UI déconnectée de la DB

Cherche tout formulaire ou bouton d'action qui ne persiste pas ses données en base.

Patterns à détecter :
- Composant avec un `onSubmit` ou `onPress` qui ne contient aucun appel API / ORM / mutation (`fetch`, `axios`, appel au client DB, mutation GraphQL, etc.)
- Handler qui met à jour uniquement un state local (`setState`, `useState`) sans appel persistant
- Bouton avec `onClick` qui déclenche une navigation (`router.push`) sans appel API préalable
- Composant qui affiche un message de succès ("Envoyé", "Sauvegardé") sans appel API confirmé dans le même handler

Pour chaque occurrence, vérifie le flux complet : bouton → handler → appel API → confirmation.

### Risque 2 — Schéma DB incohérent avec le code

Compare les fichiers de migration et les types TypeScript générés.

Vérifie :
- Chaque colonne présente dans les fichiers de migration existe-t-elle dans le fichier de types généré ?
- Chaque champ utilisé dans le code correspond-il à une colonne réelle en DB ?
- Les types correspondent-ils (ex : colonne `integer` en DB mais type `string` en TypeScript) ?
- Les colonnes `NOT NULL` en DB ont-elles un champ obligatoire correspondant dans les schémas de validation (Zod ou équivalent) ?

Cherche les accès à des propriétés potentiellement inexistantes : `data?.champ_inconnu`, champs utilisés dans le JSX mais absents des types.

### Risque 3 — Échec silencieux sur les appels DB

Cherche tout appel au client DB / ORM où le retour n'est pas pleinement vérifié.

Patterns problématiques :
```typescript
// Pas de vérification d'erreur
const { data } = await db.query('matches')

// Erreur destructurée mais jamais vérifiée
const { data, error } = await db.insert('matches', payload)
router.push('/success') // redirige même si error !== null
```

Pattern correct attendu :
```typescript
const { data, error } = await db.insert('matches', payload)
if (error) { /* gestion explicite */ return }
```

### Risque 4 — Données mockées laissées en production

Cherche toute fixture ou donnée de test qui pourrait être affichée à un vrai utilisateur.

Patterns : `const fakeData`, `const mockData`, `const dummyData`, `const testData`, tableaux de données statiques dans des composants de page (pas dans des fichiers `*.test.*` ou `*.stories.*`), `TODO: replace with real data`, `// temp`, `// hardcoded for now`.

### Risque 5 — Opérations multi-tables sans transaction

Cherche les flux qui écrivent dans plusieurs tables successivement sans mécanisme transactionnel.

Patterns : deux appels insert ou update séquentiels dans le même handler sans rollback en cas d'échec du second, création d'entités liées (ex : créer une entité parente + créer l'entité enfant) avec des inserts séparés.

---

## Catégorie 2 — Auth & accès

### Risque 6 — Policies d'accès absentes ou mal configurées

Pour chaque table identifiée dans les fichiers de migration, vérifie :
- Est-ce que la Row Level Security (RLS) ou équivalent est activée ? (RLS est une fonctionnalité PostgreSQL qui restreint les lignes accessibles par requête selon l'identité de l'appelant)
- Est-ce qu'au moins une policy `SELECT`, `INSERT`, `UPDATE`, `DELETE` est définie ?
- Est-ce que la policy contient `USING (true)` ou `WITH CHECK (true)` sans condition (accès permissif total) ?
- Est-ce que la policy vérifie bien l'identité de l'utilisateur pour isoler les données par utilisateur / tenant ?

Liste chaque table avec son statut : activé / désactivé / activé mais permissif.

### Risque 7 — Vérification de rôle uniquement côté UI

Cherche les cas où un rôle est vérifié dans l'UI mais pas dans la couche API ou les policies d'accès.

Patterns UI-only :
```typescript
if (role !== 'coach') return <Redirect to="/login" />
{role === 'admin' && <AdminPanel />}
```

Pour chaque vérification de rôle côté UI, vérifie qu'il existe une vérification équivalente dans la route API correspondante ou dans une policy d'accès côté base de données.

### Risque 8 — Middleware d'auth incomplet

Examine le fichier de middleware d'authentification du framework web.

Vérifie :
- Modèle whitelist (risqué — tout est bloqué sauf liste explicite) ou blacklist (sûr — tout est autorisé sauf liste explicite) ?
- Toutes les routes protégées (tableau de bord, admin, espace personnel) sont-elles couvertes ?
- Les routes API sont-elles protégées ?
- Des routes récentes non encore ajoutées au middleware ?

Compare la liste des routes de l'app avec les routes couvertes par le middleware.

### Risque 9 — Session expirée sans gestion

Vérifie :
- Le client d'authentification est-il configuré avec le refresh automatique des tokens ?
- Y a-t-il un listener sur les changements d'état d'auth qui redirige vers le login si la session expire ?
- Les erreurs `401` sont-elles interceptées globalement ?
- Sur mobile (si applicable), le token est-il persisté dans un stockage sécurisé (SecureStore ou équivalent) et non dans un stockage non chiffré ?

---

## Format du rapport — AUDIT_COMPORTEMENTAL_A1.md

```markdown
# Audit comportemental — Session A1/3 : Données & DB + Auth & accès
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X

---

## Catégorie 1 — Données & DB

### Risque 1 — UI déconnectée de la DB
| Sévérité | Fichier | Ligne | Description | Action |
|----------|---------|-------|-------------|--------|

### Risque 2 — Schéma DB incohérent
| Sévérité | Champ/Table | Fichier | Problème constaté |
|----------|-------------|---------|------------------|

### Risque 3 — Échec silencieux sur appels DB
| Sévérité | Fichier | Ligne | Code problématique |
|----------|---------|-------|-------------------|

### Risque 4 — Données mockées en prod
| Sévérité | Fichier | Ligne | Variable/Valeur |
|----------|---------|-------|----------------|

### Risque 5 — Opérations multi-tables sans transaction
| Sévérité | Fichier | Lignes | Tables concernées |
|----------|---------|--------|------------------|

---

## Catégorie 2 — Auth & accès

### Risque 6 — Policies d'accès absentes ou mal configurées
| Table | RLS/Policy activée | Policies définies | Problème |
|-------|-------------------|------------------|----------|

### Risque 7 — Vérification de rôle UI-only
| Sévérité | Fichier UI | Ligne | Protégée côté serveur ? |
|----------|-----------|-------|-------------------------|

### Risque 8 — Middleware d'auth incomplet
| Route | Couverte ? | Problème |
|-------|-----------|----------|

### Risque 9 — Session expirée sans gestion
| Sévérité | Point de contrôle | Statut |
|----------|------------------|--------|
```
