# Session C3/3 — Audit qualité code : Requêtes DB + SQL & migrations

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **2 catégories sur 7** — toute la couche données. Lance-la dans une nouvelle session Claude Code, indépendamment de C1 et C2.

Fichier de sortie à générer : `AUDIT_QUALITE_C3.md`

---

## Catégorie 4 — Requêtes DB / ORM

### 4A. select('*') systématique

Cherche tous les appels qui sélectionnent toutes les colonnes sans liste explicite (`select('*')` ou `select()` sans colonnes).

Pour chaque occurrence, identifie quelles colonnes sont réellement utilisées dans le composant ou la fonction — c'est ce qui devrait être dans le `select()`.

### 4B. Requêtes N+1

Cherche les patterns où une première requête retourne une liste, puis une deuxième requête est faite pour chaque item dans une boucle.

Pattern problématique :
```typescript
// N+1 — 1 requête pour les parents + 1 par parent pour ses enfants
const parents = await db.from('parents').select()
for (const parent of parents.data) {
  const children = await db.from('children').select().eq('parent_id', parent.id)
}

// Correct — 1 seule requête avec join
const parents = await db.from('parents').select('*, children(*)')
```

Cherche : boucles `for`, `forEach`, `map` contenant des appels DB ou `await`.

### 4C. Absence d'index sur les colonnes filtrées

Examine les migrations SQL et identifie les colonnes utilisées dans des filtres (`.eq()`, `.filter()`, `.order()`, ou équivalents ORM).

Vérifie pour chacune si un index existe dans les migrations :
```sql
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_created_at ON items(created_at DESC);
```

Liste les colonnes fréquemment filtrées sans index correspondant.

### 4D. Subscriptions temps-réel non désabonnées

Si le projet utilise des subscriptions temps-réel (WebSockets, Realtime), cherche tous les abonnements et vérifie que chacun a un désabonnement dans la fonction de cleanup du `useEffect`.

### 4E. Requêtes sans limite de résultats

Cherche les requêtes qui retournent potentiellement des milliers de lignes sans `.limit()` ni pagination.

Signale chaque requête sur des tables qui peuvent croître sans limite (tables de contenu principal, logs, événements) sans pagination explicite.

### 4F. Requêtes identiques dupliquées

Compare toutes les requêtes DB dans le codebase. Cherche les requêtes qui fetchent les mêmes données (même table, mêmes filtres) à plusieurs endroits sans couche de cache ou service partagé.

---

## Catégorie 5 — SQL & migrations

### 5A. Migrations non idempotentes

Examine chaque fichier de migration.

Vérifie que chaque statement utilise les gardes appropriées :
```sql
-- Correct
CREATE TABLE IF NOT EXISTS items (...);
CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id);
ALTER TABLE items ADD COLUMN IF NOT EXISTS status integer;

-- Problématique — crash si rejoué
CREATE TABLE items (...);
```

### 5B. Colonnes sans contraintes appropriées

Examine le schéma de chaque table. Vérifie :
- Les colonnes obligatoires ont-elles `NOT NULL` ?
- Les colonnes avec valeurs prédéfinies ont-elles des `CHECK` constraints ?
  ```sql
  CHECK (status IN (1, 2, 3))
  CHECK (role IN ('admin', 'user', 'manager'))
  ```
- Les clés étrangères ont-elles `REFERENCES` avec `ON DELETE` défini ?
- Les colonnes de dates ont-elles des valeurs par défaut (`DEFAULT NOW()`) ?

### 5C. Absence de timestamps standards

Vérifie que chaque table métier a :
```sql
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

Et qu'un trigger `updated_at` est défini pour la mise à jour automatique.

### 5D. Nommage incohérent

Vérifie la cohérence du nommage dans le schéma SQL :
- Tables en `snake_case` pluriel ? (`items`, `user_groups`, non `Item` ou `UserGroup`)
- Colonnes en `snake_case` ? (`user_id`, non `userId`)
- Index avec convention cohérente ? (`idx_[table]_[colonne]`)
- Fonctions SQL avec convention ? (`get_`, `set_`, `handle_`)

### 5E. Fonctions SQL trop complexes

Examine les fonctions PostgreSQL dans les migrations ou les Edge Functions.

Signale les fonctions qui :
- Dépassent 50 lignes sans commentaire de structure
- Contiennent des sous-requêtes imbriquées sur plus de 3 niveaux
- Mélangent logique métier et logique d'accès aux données
- N'ont pas de type de retour explicitement déclaré

### 5F. Policies d'accès (Row Level Security) mal optimisées

Si le projet utilise PostgreSQL avec Row Level Security (RLS — mécanisme de PostgreSQL qui filtre les lignes selon l'identité de l'appelant), examine chaque policy.

Vérifie :
- Les policies font-elles des sous-requêtes coûteuses à chaque appel ?
- Utilisent-elles l'identifiant utilisateur directement (indexé) ou des jointures inutiles ?
- Y a-t-il des policies redondantes sur la même table ?

Pattern optimisé vs sous-optimal :
```sql
-- Optimal — identifiant direct
CREATE POLICY "user_sees_own_items" ON items
  FOR SELECT USING (user_id = auth.uid());

-- Sous-optimal — sous-requête à chaque appel
CREATE POLICY "user_sees_own_items" ON items
  FOR SELECT USING (
    user_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
  );
```

---

## Format du rapport — AUDIT_QUALITE_C3.md

```markdown
# Audit qualité code — Session C3/3 : Requêtes DB + SQL & migrations
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X | Informatif : X

---

## Catégorie 4 — Requêtes DB / ORM

### 4A. select('*') systématique
| Fichier | Ligne | Table | Colonnes réellement utilisées |
|---------|-------|-------|------------------------------|

### 4B. Requêtes N+1
| Sévérité | Fichier | Lignes | Tables concernées | Correction |
|----------|---------|--------|------------------|-----------|

### 4C. Index manquants
| Colonne | Table | Utilisée dans | Index présent ? |
|---------|-------|--------------|----------------|

### 4D. Subscriptions non désabonnées
| Sévérité | Fichier | Ligne | Channel/Topic | Cleanup présent ? |
|----------|---------|-------|--------------|------------------|

### 4E. Requêtes sans limite
| Fichier | Ligne | Table | Risque volumétrique |
|---------|-------|-------|---------------------|

### 4F. Requêtes dupliquées
| Requête | Fichiers concernés | Correction suggérée |
|---------|--------------------|---------------------|

---

## Catégorie 5 — SQL & migrations

### 5A. Migrations non idempotentes
| Fichier migration | Ligne | Statement problématique |
|------------------|-------|------------------------|

### 5B. Colonnes sans contraintes
| Table | Colonne | Contrainte manquante |
|-------|---------|---------------------|

### 5C. Timestamps manquants
| Table | created_at ? | updated_at ? | Trigger ? |
|-------|-------------|-------------|----------|

### 5D. Nommage incohérent
| Fichier | Élément | Convention attendue | Convention utilisée |
|---------|---------|--------------------|--------------------|

### 5E. Fonctions SQL trop complexes
| Fonction | Fichier | Lignes | Problème |
|---------|---------|--------|---------|

### 5F. Policies RLS mal optimisées
| Table | Policy | Problème | Correction |
|-------|--------|---------|-----------|
```
