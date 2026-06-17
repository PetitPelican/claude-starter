# Session A2/3 — Audit comportemental : Architecture + UX silencieuse

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **2 catégories sur 5**. Lance-la dans une nouvelle session Claude Code, indépendamment de A1.

Fichier de sortie à générer : `AUDIT_COMPORTEMENTAL_A2.md`

---

## Catégorie 3 — Architecture

### Risque 10 — Logique métier dupliquée entre mobile et web

Cherche les règles métier implémentées séparément dans `apps/[FRAMEWORK_MOBILE]` et `apps/[FRAMEWORK_WEB]` au lieu d'être dans `packages/`.

Règles à vérifier :
- Validation des formulaires (champs obligatoires, formats, limites)
- Vérification des limites par plan / abonnement (max utilisateurs, quotas)
- Formatage des données d'affichage (classements, statistiques, scores)
- Calculs d'agrégation pour les tableaux de bord

Pour chaque règle dupliquée, indique si les deux versions sont identiques ou divergentes.

### Risque 11 — Types TypeScript non partagés

Cherche les types redéfinis localement dans chaque app au lieu d'être importés de `packages/types`.

Patterns : fichiers `types.ts` ou `interfaces.ts` dans `apps/[FRAMEWORK_MOBILE]/` ou `apps/[FRAMEWORK_WEB]/` qui redéfinissent des entités centrales du domaine métier.

Pour chaque type redéfini localement, compare-le avec la définition dans `packages/types` — sont-ils synchronisés ?

### Risque 12 — Pas de gestion offline sur mobile

Si le projet comporte une application mobile, examine-la pour la gestion des soumissions en cas de réseau instable.

Vérifie :
- Y a-t-il une détection de connectivité avant la soumission d'un formulaire ?
- En cas d'échec réseau, le formulaire est-il mis en queue locale (stockage local) pour retry ?
- L'utilisateur reçoit-il un feedback explicite ?
- Y a-t-il un mécanisme de retry automatique au retour du réseau ?

### Risque 13 — Imports circulaires entre packages

Pour chaque package dans `packages/`, vérifie ses imports et détecte les cycles.

- Un package importe-t-il depuis un autre package qui l'importe en retour ?
- Un package `ui` importe-t-il depuis un package `db` directement ?

Si le projet utilise un gestionnaire de monorepo (Turborepo, Nx, etc.), vérifie que les dépendances déclarées dans la configuration correspondent aux imports réels.

### Risque 14 — Appels DB directs dans les composants UI

Cherche les appels au client DB / ORM effectués directement dans des composants React ou des pages, sans couche service/repository.

Pattern problématique :
```typescript
useEffect(() => {
  db.from('matches').select().then(...)
}, [])
```

Compte le nombre d'occurrences et identifie les requêtes dupliquées (même table, filtre similaire, dans plusieurs composants).

---

## Catégorie 4 — UX silencieuse

### Risque 15 — États de chargement absents

Cherche les composants qui font des appels API sans afficher d'état de chargement.

Patterns : composant avec `useEffect` + appel API mais sans variable `isLoading` / `isPending`, absence de skeleton loader ou spinner, liste vide pendant le chargement sans distinction avec un vrai empty state.

Vérifie en particulier :
- Les tableaux de bord (chargement des données principales)
- Les formulaires de soumission
- Les listes d'entités (utilisateurs, éléments de contenu)

### Risque 16 — Actions destructives sans confirmation

Cherche les handlers de suppression branchés directement sans étape de confirmation.

Pattern problématique :
```typescript
<button onClick={() => db.from('groups').delete().eq('id', groupId)}>
  Supprimer
</button>
```

Cherche : `onClick` ou `onPress` contenant `delete`, `remove`, `destroy`, ou un appel DB `.delete()` sans modale de confirmation.

### Risque 17 — Validation formulaire absente ou incomplète

Pour chaque formulaire identifié, vérifie :
- Y a-t-il un schéma de validation défini (Zod, Yup, Valibot ou équivalent) ?
- La validation est-elle exécutée avant l'appel API ?
- Les erreurs de validation sont-elles affichées champ par champ ?
- La validation côté client est-elle cohérente avec les contraintes DB ?

Formulaires critiques : création de compte, formulaire principal de l'app, formulaires d'administration.

### Risque 18 — Empty states non gérés

Cherche les composants qui affichent une liste sans gérer le cas où les données sont vides.

Patterns : `{data.map(...)}` sans vérification `data.length === 0`, page avec conteneur vide sans message ni call-to-action.

Vérifie en particulier :
- Tableaux de bord d'un nouveau compte (aucune donnée)
- Listes de contenu en début d'utilisation
- Résultats de recherche sans correspondance

---

## Format du rapport — AUDIT_COMPORTEMENTAL_A2.md

```markdown
# Audit comportemental — Session A2/3 : Architecture + UX silencieuse
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X

---

## Catégorie 3 — Architecture

### Risque 10 — Logique métier dupliquée
| Règle métier | Fichier mobile | Fichier web | Synchronisés ? |
|-------------|----------------|-------------|---------------|

### Risque 11 — Types non partagés
| Type | Défini mobile ? | Défini web ? | Cohérents avec packages/types ? |
|------|----------------|-------------|--------------------------------|

### Risque 12 — Pas de gestion offline
| Sévérité | Point de contrôle | Statut |
|----------|------------------|--------|

### Risque 13 — Imports circulaires
| Package source | Importe | Qui importe en retour | Cycle ? |
|---------------|---------|----------------------|---------|

### Risque 14 — Appels DB dans les composants
| Fichier | Ligne | Table/Ressource requêtée | Dupliqué ailleurs ? |
|---------|-------|--------------------------|---------------------|

---

## Catégorie 4 — UX silencieuse

### Risque 15 — États de chargement absents
| Sévérité | Composant | Fichier | Appel API sans loader |
|----------|-----------|---------|----------------------|

### Risque 16 — Actions destructives sans confirmation
| Sévérité | Fichier | Ligne | Action |
|----------|---------|-------|--------|

### Risque 17 — Validation formulaire absente
| Formulaire | Fichier | Schéma validation ? | Validation avant API ? | Erreurs affichées ? |
|-----------|---------|--------------------|-----------------------|---------------------|

### Risque 18 — Empty states non gérés
| Sévérité | Composant | Fichier | Données concernées |
|----------|-----------|---------|-------------------|
```
