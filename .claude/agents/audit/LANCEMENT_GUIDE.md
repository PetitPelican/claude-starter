# Guide de lancement — Sessions d'audit

## Vue d'ensemble

3 audits, 8 sessions au total, 8 fichiers de rapport produits.

```
Audit A — Comportemental (ce que l'app fait)
  ├── A1 : Données & DB + Auth & accès         → AUDIT_COMPORTEMENTAL_A1.md
  ├── A2 : Architecture + UX silencieuse       → AUDIT_COMPORTEMENTAL_A2.md
  └── A3 : Ops & prod                          → AUDIT_COMPORTEMENTAL_A3.md

Audit B — Transversal (dette structurelle)
  ├── B1 : Valeurs hardcodées + Tests absents  → AUDIT_TRANSVERSAL_B1.md
  └── B2 : Gestion des erreurs + Logging       → AUDIT_TRANSVERSAL_B2.md

Audit C — Qualité du code (comment c'est écrit)
  ├── C1 : TypeScript + Structure              → AUDIT_QUALITE_C1.md
  ├── C2 : React/[FRAMEWORK_WEB] + [FRAMEWORK_MOBILE] + Perf web → AUDIT_QUALITE_C2.md
  └── C3 : Requêtes DB + SQL & migrations      → AUDIT_QUALITE_C3.md
```

---

## Instructions de lancement

### Pour chaque session

1. **Ouvre une nouvelle session Claude Code** — ne réutilise pas une session existante
2. **Colle d'abord le contenu de `_HEADER_COMMUN.md`** intégralement
3. **Colle ensuite le contenu du fichier de session** (A1, A2, etc.)
4. Lance

### Ordre recommandé

Lance les sessions dans cet ordre de priorité :

**Priorité 1 — Sécurité et données (bloquant pour la prod)**
- A1 (Données & DB + Auth)
- A3 (Ops & prod)
- B1 (Hardcoded + Tests) — pour les clés en dur

**Priorité 2 — Bugs utilisateurs**
- A2 (Architecture + UX)
- B2 (Erreurs + Logging)

**Priorité 3 — Qualité du code**
- C3 (DB + SQL) — SQL est critique pour les perfs
- C1 (TypeScript + Structure)
- C2 (React + [FRAMEWORK_MOBILE] + Perf)

### Parallélisation possible

Les sessions d'un même audit ne se chevauchent pas — elles peuvent tourner en parallèle si tu as plusieurs instances Claude Code disponibles :
- A1 + A2 + A3 peuvent tourner simultanément
- B1 + B2 peuvent tourner simultanément
- C1 + C2 + C3 peuvent tourner simultanément

---

## Si Claude Code s'arrête en cours de route

Le header commun lui demande de s'arrêter et de signaler sa position exacte plutôt que de comprimer. Si ça arrive :

1. Note le dernier fichier qu'il a traité
2. Relance une nouvelle session avec le même prompt de session
3. Ajoute cette instruction au début : **"Reprends l'audit à partir du fichier `[nom du fichier]`. Les fichiers précédents ont déjà été audités dans une session précédente, ne les retraite pas."**
4. À la fin, fusionne manuellement les deux rapports partiels

---

## Consolidation finale (optionnelle)

Une fois les 8 sessions terminées, tu peux lancer une session de consolidation avec ce prompt :

```
Tu as 8 fichiers de rapport d'audit dans ce projet :
AUDIT_COMPORTEMENTAL_A1.md, A2.md, A3.md
AUDIT_TRANSVERSAL_B1.md, B2.md
AUDIT_QUALITE_C1.md, C2.md, C3.md

Lis-les tous et génère un fichier AUDIT_SYNTHESE.md qui contient :

1. Un tableau de bord global : total des occurrences par sévérité (Critique / Élevé / Moyen)
   par audit et au global.

2. Le top 10 des problèmes les plus critiques toutes catégories confondues,
   classés par impact réel sur les utilisateurs ou la sécurité.

3. Un plan d'action en 3 sprints :
   - Sprint Sécurité (Critiques uniquement — à faire avant tout déploiement)
   - Sprint Stabilité (Élevés — à faire avant la première démonstration)
   - Sprint Dette (Moyens — backlog structurel)

Ne modifie aucun fichier de rapport existant.
```
