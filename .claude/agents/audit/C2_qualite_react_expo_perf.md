# Session C2/3 — Audit qualité code : React/[FRAMEWORK_WEB] + [FRAMEWORK_MOBILE] + Performance web

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **3 catégories sur 7** — toute la couche UI. Lance-la dans une nouvelle session Claude Code, indépendamment de C1 et C3.

Fichier de sortie à générer : `AUDIT_QUALITE_C2.md`

---

## Catégorie 2 — React & composants

### 2A. Composants trop larges

Cherche les composants dépassant 150 lignes ou gérant plusieurs responsabilités.

Pour chaque composant identifié :
- Nombre de responsabilités distinctes (fetch + affichage + soumission + validation = 4)
- Parties pouvant être extraites en sous-composants ou hooks

### 2B. Re-renders inutiles

Patterns :
- Objets créés inline passés comme props (`<Component config={{ key: 'value' }} />`)
- Fonctions créées inline sans `useCallback` (`<Component onChange={() => setValue(...)} />`)
- Calculs coûteux dans le corps du composant sans `useMemo`
- Context dont la valeur est un objet recréé sans `useMemo`

### 2C. useEffect mal utilisé

Patterns :
- Dépendances manquantes dans le tableau
- Dépendances trop larges
- `useEffect` pour de la logique de dérivation (devrait être `useMemo`)
- `useEffect` sans cleanup pour subscriptions, listeners, ou timers
- `useEffect` avec `[]` vide qui contient des références extérieures

### 2D. 'use client' abusif (si framework web avec Server Components)

Si le framework web supporte les Server Components (ex : Next.js App Router), examine tous les fichiers contenant `'use client'`.

Pour chaque fichier, vérifie si `'use client'` est justifié :
- Utilise-t-il des hooks React (`useState`, `useEffect`, `useRef`) ? → justifié
- Utilise-t-il des événements browser (`onClick`, `onChange`) ? → justifié
- Ne fait-il qu'afficher des données reçues en props ? → probablement inutile

### 2E. Fetch de données côté client au lieu du serveur

Si le framework web supporte les Server Components, cherche les `useEffect` + `fetch` ou `useEffect` + requête DB dans des composants de page qui pourraient être des Server Components.

Pattern problématique :
```typescript
'use client'
export default function Dashboard() {
  const [items, setItems] = useState([])
  useEffect(() => {
    db.from('items').select().then(setItems)
  }, [])
}

// Correct — Server Component
export default async function Dashboard() {
  const items = await getItems()
  return <ItemList items={items} />
}
```

### 2F. Props drilling excessif

Cherche les props passées à travers plus de 2 niveaux de composants intermédiaires sans utilité propre à ces intermédiaires.

Si une prop traverse 3 composants ou plus sans être utilisée par les intermédiaires → props drilling à corriger (Context, restructuration).

---

## Catégorie 3 — Framework mobile (si applicable)

Si le projet ne comporte pas d'application mobile, marque toute cette catégorie "Non applicable".

### 3A. ScrollView sur listes longues

Cherche les `ScrollView` wrappant un `.map()` sur des données dynamiques.

Pattern problématique :
```typescript
<ScrollView>
  {items.map(item => <ItemCard key={item.id} item={item} />)}
</ScrollView>
```

Préférer `FlatList` ou `FlashList` pour les listes dynamiques.

### 3B. Animations sans useNativeDriver

Cherche les animations Animated API sans `useNativeDriver: true`.

Cherche aussi les animations implémentées avec `useState` + `setInterval` qui devraient utiliser `Animated` ou `react-native-reanimated`.

### 3C. Images non optimisées

Vérifie :
- Une librairie d'images optimisées est-elle installée et utilisée ?
- Les images distantes ont-elles `contentFit` ou `resizeMode` défini ?
- Les images ont-elles des dimensions explicites ?

### 3D. Listeners non nettoyés

Cherche les subscriptions et listeners enregistrés dans des `useEffect` sans cleanup.

```typescript
// Problématique — fuite mémoire
useEffect(() => {
  const subscription = client.channel('items').on(...).subscribe()
  AppState.addEventListener('change', handler)
  // pas de return cleanup
}, [])
```

### 3E. Accès direct aux dimensions écran

Cherche les usages de `Dimensions.get('window')` dans des composants sans écouter les changements.

Préférer : `useWindowDimensions()` hook qui se met à jour automatiquement.

---

## Catégorie 7 — Performance web

### 7A. Images non optimisées

Cherche les `<img>` HTML classiques au lieu du composant image optimisé du framework.

Vérifie que les images optimisées ont :
- `width` et `height` explicites ou `fill` avec conteneur positionné
- `priority` sur les images above-the-fold
- `alt` descriptif (pas vide, pas "image")

### 7B. Fonts non optimisées

Vérifie si les polices utilisent le système d'optimisation du framework (ex : `next/font`) ou un `<link>` externe dans le `<head>` (non optimisé).

### 7C. Métadonnées SEO absentes

Vérifie :
- Chaque page a-t-elle des métadonnées avec `title` et `description` ?
- Le layout racine a-t-il des métadonnées par défaut ?
- Y a-t-il un `robots.txt` et un `sitemap.xml` ?

### 7D. Bundle JavaScript non optimisé

Patterns problématiques :
```typescript
// Import de toute la lib
import * as Icons from 'lucide-react'
import _ from 'lodash'
import * as dateFns from 'date-fns'

// Correct — tree-shakeable
import { ChevronRight, User } from 'lucide-react'
import { format } from 'date-fns'
```

---

## Format du rapport — AUDIT_QUALITE_C2.md

```markdown
# Audit qualité code — Session C2/3 : React/[FRAMEWORK_WEB] + [FRAMEWORK_MOBILE] + Performance web
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X | Informatif : X

---

## Catégorie 2 — React & composants

### 2A. Composants trop larges
| Fichier | Lignes | Responsabilités | Proposition |
|---------|--------|----------------|------------|

### 2B. Re-renders inutiles
| Sévérité | Fichier | Ligne | Pattern | Correction |
|----------|---------|-------|---------|-----------|

### 2C. useEffect mal utilisé
| Sévérité | Fichier | Ligne | Problème | Correction |
|----------|---------|-------|----------|-----------|

### 2D. 'use client' abusif
| Fichier | Justifié ? | Raison |
|---------|-----------|--------|

### 2E. Fetch côté client au lieu du serveur
| Fichier | Ligne | Données fetchées | Impact |
|---------|-------|-----------------|--------|

### 2F. Props drilling
| Prop | Fichier source | Profondeur | Correction |
|------|---------------|-----------|-----------|

---

## Catégorie 3 — Framework mobile

### 3A. ScrollView sur listes dynamiques
| Fichier | Ligne | Données affichées | Impact |
|---------|-------|------------------|--------|

### 3B. Animations sans useNativeDriver
| Fichier | Ligne | Type d'animation |
|---------|-------|-----------------|

### 3C. Images non optimisées
| Fichier | Ligne | Problème |
|---------|-------|---------|

### 3D. Listeners non nettoyés
| Sévérité | Fichier | Ligne | Listener | Cleanup présent ? |
|----------|---------|-------|----------|------------------|

### 3E. Dimensions écran statiques
| Fichier | Ligne | Correction |
|---------|-------|-----------|

---

## Catégorie 7 — Performance web

### 7A. Images non optimisées
| Fichier | Ligne | Problème | Correction |
|---------|-------|---------|-----------|

### 7B. Fonts non optimisées
| Fichier | Méthode actuelle | Correction |
|---------|-----------------|-----------|

### 7C. Métadonnées SEO
| Page | title ? | description ? | Problème |
|------|--------|--------------|---------|

### 7D. Bundle non optimisé
| Fichier | Ligne | Import problématique | Impact |
|---------|-------|---------------------|--------|
```
