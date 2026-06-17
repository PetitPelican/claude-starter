# Session B1/2 — Audit transversal : Valeurs hardcodées + Tests absents

## Initialisation

Avant toute chose, lis le fichier `.claude/agents/audit/prompt audit/_HEADER_COMMUN.md` intégralement. Ce fichier contient le contexte projet, les règles d'audit et les instructions de cartographie. Applique toutes ses instructions avant de commencer l'audit ci-dessous.

Cette session couvre **2 catégories sur 4**. Lance-la dans une nouvelle session Claude Code, indépendamment de B2.

Fichier de sortie à générer : `AUDIT_TRANSVERSAL_B1.md`

---

## Catégorie 1 — Valeurs hardcodées

### 1A. Couleurs

Signale toute couleur définie en dur hors du fichier de configuration du système de styles et hors des tokens de design.

Patterns : `#[0-9a-fA-F]{3,8}`, `rgb(`, `rgba(`, `color: 'red'`, `backgroundColor: 'white'`, classes arbitraires `bg-[#...]`, `text-[#...]`, `StyleSheet.create` avec couleurs nommées.

Exceptions acceptées : fichier de configuration du système de styles, fichier de variables CSS de base (`globals.css` ou équivalent), fichiers de migration SQL.

### 1B. Espacements & typographie

Signale toute valeur de taille définie en dur hors du système de styles.

Patterns : `style={{ padding: 16 }}`, `marginTop: 24`, `fontSize: 14`, `height: 48`, `borderRadius: 8`, `lineHeight`, `letterSpacing`, `fontWeight` inline, durées d'animation `duration: 200`, `zIndex` numérique inline, classes arbitraires `p-[16px]`, `h-[48px]`.

### 1C. Constantes métier

Signale toute règle métier définie en dur dans un composant ou une page au lieu d'être dans un fichier de constantes centralisé.

Patterns génériques :
- Listes d'options définies inline (catégories, statuts, niveaux, types)
- États ou valeurs énumérées : `["actif", "inactif", "suspendu"]`
- Prix ou montants dans de la logique métier
- Noms de plans ou d'offres tarifaires
- Limites quantitatives par plan (quotas, maximums)
- Rôles en dur hors fichier de constantes : `"admin"`, `"user"`, `"manager"`
- Listes de valeurs du domaine métier définis inline

### 1D. Clés & URLs d'infrastructure

Signale tout identifiant externe hors `process.env`.

Patterns : tokens JWT (`eyJ`), URLs de services externes en dur dans du code logique, clés publiques ou privées de provider de paiements (`pk_live_`, `pk_test_`, `sk_live_`, `sk_test_`), secrets de webhook (`whsec_`), identifiants de prix (`price_`), URLs de l'application en dur dans de la logique (pas dans de la documentation), emails en dur hors templates.

### 1E. Textes UI

Signale tout texte utilisateur défini inline dans les composants.

Patterns : messages d'erreur inline, libellés de boutons, placeholders, toasts, messages de validation, empty states, textes d'emails transactionnels dans le code.

### 1F. Configuration technique

Patterns : `setTimeout(..., 3000)`, `maxAge: 3600`, `.limit(20)`, `pageSize = 50`, `5 * 1024 * 1024`, ports en dur, noms de tables DB répétés sans constante centralisée, noms de buckets de stockage, noms de topics temps-réel.

---

## Catégorie 2 — Tests absents

### 2A. Couverture globale

Vérifie si un framework de test est configuré :
- Présence de `vitest.config.ts` ou `jest.config.ts` à la racine ou dans chaque app
- Présence de scripts `"test"` dans les `package.json`
- Présence d'un dossier `__tests__/` ou de fichiers `*.test.ts` / `*.spec.ts`

Si aucun framework de test n'est configuré, signale-le comme **Critique** immédiatement.

### 2B. Logique métier sans test

Pour chaque fichier contenant de la logique métier (validations, calculs, transformations), vérifie s'il existe un fichier de test correspondant.

Priorité haute :
- Validation des formulaires principaux
- Logique de vérification des rôles et permissions
- Calculs d'agrégation pour les tableaux de bord
- Logique d'intégration avec le provider de paiements
- Fonctions utilitaires dans `packages/`

### 2C. Routes API sans test

Liste toutes les routes API et vérifie si chacune a un test d'intégration.

### 2D. Policies d'accès sans test

Vérifie si les migrations SQL contiennent des policies d'accès (Row Level Security ou équivalent) et si un dossier de tests existe pour les valider.

---

## Format du rapport — AUDIT_TRANSVERSAL_B1.md

```markdown
# Audit transversal — Session B1/2 : Valeurs hardcodées + Tests absents
Date : [date]

## Résumé de session
- Fichiers analysés : X
- Critique : X | Élevé : X | Moyen : X

---

## Catégorie 1 — Valeurs hardcodées

### 1A. Couleurs
| Sévérité | Fichier | Ligne | Valeur | Action recommandée |
|----------|---------|-------|--------|-------------------|

### 1B. Espacements & typographie
| Sévérité | Fichier | Ligne | Valeur | Action recommandée |
|----------|---------|-------|--------|-------------------|

### 1C. Constantes métier
| Sévérité | Fichier | Ligne | Valeur | Action recommandée |
|----------|---------|-------|--------|-------------------|

### 1D. Clés & URLs
| Sévérité | Fichier | Ligne | Valeur | Action recommandée |
|----------|---------|-------|--------|-------------------|

### 1E. Textes UI
| Sévérité | Fichier | Ligne | Texte | Action recommandée |
|----------|---------|-------|-------|-------------------|

### 1F. Configuration technique
| Sévérité | Fichier | Ligne | Valeur | Action recommandée |
|----------|---------|-------|--------|-------------------|

---

## Catégorie 2 — Tests absents

### 2A. Framework de test
[présent / absent + détail]

### 2B. Logique métier sans test
| Sévérité | Fichier logique | Fichier test attendu | Statut |
|----------|----------------|---------------------|--------|

### 2C. Routes API sans test
| Route | Fichier test attendu | Statut |
|-------|---------------------|--------|

### 2D. Policies d'accès sans test
| Table | Policy | Fichier test attendu | Statut |
|-------|--------|---------------------|--------|
```
