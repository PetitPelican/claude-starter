# Session B2/2 — Audit transversal : Gestion des erreurs + Logging & observabilité

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **2 catégories sur 4**. Lance-la dans une nouvelle session Claude Code, indépendamment de B1.

Fichier de sortie à générer : `AUDIT_TRANSVERSAL_B2.md`

---

## Catégorie 3 — Gestion des erreurs

### 3A. Appels DB / API sans vérification d'erreur

Cherche tout appel au client DB ou ORM où l'erreur n'est pas vérifiée après la destructuration.

Pattern à détecter :
```typescript
// Problématique — erreur ignorée
const { data } = await db.query('matches')

// Problématique — erreur destructurée mais jamais lue
const { data, error } = await db.insert('matches', payload)
router.push('/success') // redirige même si error !== null

// Correct
const { data, error } = await db.query('matches')
if (error) throw error
```

### 3B. Appels fetch/API sans try-catch

Cherche tout `fetch(`, `axios.`, ou appel de fonction async dans un composant ou handler sans bloc `try/catch` ou `.catch()`.

### 3C. Formulaires sans gestion d'erreur de soumission

Cherche les handlers `onSubmit` qui appellent une API sans bloc `catch` et sans état `error` affiché à l'utilisateur.

Pattern problématique :
```typescript
const handleSubmit = async () => {
  await db.insert(data) // pas de try/catch, pas d'error state
  router.push('/success')
}
```

### 3D. Promesses non gérées

Cherche les appels async sans `await` et sans `.catch()` — la promesse échoue silencieusement.

Patterns : appels au client DB sans `await`, `fetch(...)` sans `await` dans un contexte async.

### 3E. États d'erreur capturés mais non affichés

Cherche les composants qui ont un état `error` en local state mais ne le rendent jamais dans le JSX.

```typescript
// Problématique — erreur capturée mais avalée
const [error, setError] = useState(null)
try { ... } catch(e) { setError(e) }
// ... pas de {error && <ErrorMessage />} dans le JSX
```

### 3F. Actions destructives sans confirmation

Cherche les handlers de suppression branchés directement sur un bouton sans modale de confirmation.

Pattern : `onClick={() => db.from('...').delete()...}` sans confirmation intermédiaire.

---

## Catégorie 4 — Logging & observabilité

### 4A. Console.log en prod

Cherche tous les `console.log(`, `console.warn(`, `console.error(`, `console.debug(` dans le code source hors fichiers de test.

Pour chaque occurrence, note si elle contient des données sensibles (user, token, session, email, data) — ces occurrences sont **Critiques**.

### 4B. Absence d'outil de tracking d'erreurs

Vérifie si Sentry ou un équivalent est configuré :
- Présence du package de tracking d'erreurs dans les `package.json`
- Présence des fichiers de configuration (client, serveur)
- Présence d'un `SENTRY_DSN` ou équivalent dans les `.env.example`

Si absent, signale-le comme **Élevé**.

### 4C. Absence de logs structurés côté serveur

Vérifie les routes API : est-ce qu'elles loguent les erreurs de manière structurée (avec contexte : userId, action, timestamp) ou uniquement via `console.log` brut ?

### 4D. Webhook du provider de paiements sans logging

Si le projet intègre un provider de paiements, vérifie le handler de webhook : est-ce que chaque événement reçu est loggué avec son type et son statut de traitement (succès / échec) ?

### 4E. Absence de monitoring des performances

Vérifie si des outils de monitoring sont configurés (analytics, APM, ou équivalent). Si absent, note-le comme information (non bloquant pour le MVP).

---

## Format du rapport — AUDIT_TRANSVERSAL_B2.md

```markdown
# Audit transversal — Session B2/2 : Gestion des erreurs + Logging
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X

---

## Catégorie 3 — Gestion des erreurs

### 3A. Appels DB sans vérification d'erreur
| Sévérité | Fichier | Ligne | Code problématique |
|----------|---------|-------|-------------------|

### 3B. Appels fetch sans try-catch
| Sévérité | Fichier | Ligne | Appel concerné |
|----------|---------|-------|----------------|

### 3C. Formulaires sans gestion d'erreur
| Sévérité | Fichier | Ligne | Formulaire |
|----------|---------|-------|-----------|

### 3D. Promesses non gérées
| Sévérité | Fichier | Ligne | Promesse |
|----------|---------|-------|---------|

### 3E. Erreurs capturées mais non affichées
| Sévérité | Fichier | Ligne | État error défini ? | Rendu dans JSX ? |
|----------|---------|-------|--------------------|--------------------|

### 3F. Actions destructives sans confirmation
| Sévérité | Fichier | Ligne | Action |
|----------|---------|-------|--------|

---

## Catégorie 4 — Logging & observabilité

### 4A. Console.log en prod
| Sévérité | Fichier | Ligne | Contient données sensibles ? |
|----------|---------|-------|------------------------------|

### 4B. Tracking d'erreurs
[présent / absent + recommandation]

### 4C. Logs serveur structurés
| Route API | Logs structurés ? | Problème |
|-----------|------------------|---------|

### 4D. Webhook paiements — logging
[présent / absent + détail]

### 4E. Monitoring performances
[présent / absent — informatif]
```
