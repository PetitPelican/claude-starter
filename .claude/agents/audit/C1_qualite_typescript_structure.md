# Session C1/3 — Audit qualité code : TypeScript + Structure & organisation

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **2 catégories sur 7**. Lance-la dans une nouvelle session Claude Code, indépendamment de C2 et C3.

Fichier de sortie à générer : `AUDIT_QUALITE_C1.md`

---

## Catégorie 1 — TypeScript

### 1A. Contournements du système de types

Cherche toute tentative de désactiver ou contourner TypeScript.

Patterns :
- `any` utilisé comme type de variable, paramètre, ou retour de fonction
- `as UnType` — cast forcé (`data as Entity`, `event as any`)
- `// @ts-ignore` et `// @ts-expect-error` hors fichiers de test
- `!` (non-null assertion) sans commentaire justificatif (`user!.id`, `data!.field`)
- `object` ou `{}` comme type générique
- `Record<string, any>` quand la structure est connue
- Fonctions sans type de retour explicite sur la logique métier critique

Pour chaque occurrence, note si c'est un contournement de convenance ou légitime.

### 1B. Types trop larges ou imprécis

Patterns :
- `string` pour un champ qui devrait être un union type (`role: string` au lieu de `role: 'admin' | 'user' | 'manager'`)
- `number` pour un champ contraint (`status: number` au lieu de `status: 1 | 2 | 3`)
- Tableaux non typés (`array: []` sans type d'élément)
- Props de composants avec types trop permissifs

### 1C. Types dupliqués ou incohérents

Liste tous les fichiers contenant des `interface`, `type`, ou `enum`. Pour chaque entité métier centrale du projet, vérifie combien de définitions existent.

Signale chaque duplication et indique quelle version est canonique.

### 1D. Absence de types de retour sur les fonctions critiques

Cherche les fonctions asynchrones qui appellent le client DB ou le provider de paiements sans type de retour explicite.

Pattern problématique :
```typescript
// Retour inféré, peut changer silencieusement
async function getItems(userId: string) {
  const { data } = await db.from('items').select()
  return data
}

// Correct
async function getItems(userId: string): Promise<Item[]> {
  const { data } = await db.from('items').select()
  return data ?? []
}
```

---

## Catégorie 6 — Structure & organisation du code

### 6A. Fichiers trop longs

Cherche les fichiers dépassant 200 lignes.

Pour chaque fichier identifié :
- Nombre de lignes total
- Nombre de responsabilités distinctes
- Proposition de découpage

### 6B. Fonctions trop longues

Cherche les fonctions dépassant 40 lignes.

Pour chaque fonction :
- Nom et fichier
- Nombre de lignes
- Proposition de refactoring

### 6C. Nommage ambigu

Cherche les variables, fonctions, et composants avec des noms non descriptifs dans un scope large.

Patterns : `data`, `result`, `temp`, `item`, `val`, `obj`, `res`, `response` comme noms de variables (pas dans un destructuring immédiat), fonctions nommées `handleClick`, `doSomething`, `processData` sans précision du contexte métier.

### 6D. Logique dupliquée (DRY)

Cherche les blocs de code similaires (plus de 5 lignes) répétés dans plusieurs fichiers.

Priorité :
- Logique de formatage spécifique au domaine métier
- Logique de vérification des permissions par rôle
- Patterns de fetch DB avec gestion d'erreur
- Logique de formatage de données d'affichage

### 6E. Structure des dossiers incohérente

Examine l'organisation des dossiers dans les apps.

Vérifie :
- Composants organisés par feature ou par type ?
- Hooks dans un dossier `hooks/` dédié ou éparpillés ?
- Utilitaires dans `utils/` ou `helpers/` ou les deux ?
- Constantes dans `constants/` ou définies inline ?
- Fichiers `index.ts` de barrel exports là où utile ?

### 6F. Imports désorganisés

Ordre attendu dans chaque fichier :
1. Imports Node.js natifs
2. Imports packages externes (`react`, framework, librairies tierces)
3. Imports packages internes du monorepo (`@[project]/types`, `@[project]/ui`)
4. Imports relatifs locaux (`../components/`, `./utils`)

Signale les fichiers où cet ordre n'est pas respecté.

---

## Format du rapport — AUDIT_QUALITE_C1.md

```markdown
# Audit qualité code — Session C1/3 : TypeScript + Structure & organisation
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X | Informatif : X

---

## Catégorie 1 — TypeScript

### 1A. Contournements du système de types
| Sévérité | Fichier | Ligne | Pattern | Justifié ? |
|----------|---------|-------|---------|-----------|

### 1B. Types trop larges
| Sévérité | Fichier | Ligne | Type actuel | Type attendu |
|----------|---------|-------|-------------|-------------|

### 1C. Types dupliqués
| Entité | Fichiers où définie | Version canonique |
|--------|--------------------|--------------------|

### 1D. Fonctions sans type de retour
| Fichier | Ligne | Fonction | Type de retour attendu |
|---------|-------|----------|----------------------|

---

## Catégorie 6 — Structure & organisation

### 6A. Fichiers trop longs
| Fichier | Lignes | Responsabilités | Proposition |
|---------|--------|----------------|------------|

### 6B. Fonctions trop longues
| Fichier | Fonction | Lignes | Proposition |
|---------|----------|--------|------------|

### 6C. Nommage ambigu
| Fichier | Ligne | Nom actuel | Nom suggéré |
|---------|-------|-----------|------------|

### 6D. Logique dupliquée
| Pattern | Fichiers concernés | Où extraire |
|---------|-------------------|------------|

### 6E. Structure des dossiers
| App | Problème | Structure recommandée |
|-----|----------|-----------------------|

### 6F. Imports désorganisés
| Fichier | Problème |
|---------|---------|
```
