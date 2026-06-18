Agis comme agent mémoire du projet. Ton rôle : maintenir les fichiers `.claude/memory/` à jour avec l'état réel du projet.

## Étapes

1. **Lis les fichiers mémoire actuels**
   - `.claude/memory/MEMORY.md` — index pour savoir quels fichiers existent
   - `.claude/memory/state.md`
   - `.claude/memory/decisions.md`
   - `.claude/memory/business.md`
   - `.claude/memory/architecture.md` (si présent)
   - `.claude/memory/data-model.md` (si présent)
   - `.claude/memory/clients.md` (si présent)

2. **Lis le git log depuis la dernière mise à jour**
   ```
   git log --oneline --since="$(grep 'Dernière mise à jour' .claude/memory/state.md | head -1 | grep -oP '\d{4}-\d{2}-\d{2}')"
   ```
   Si la date est introuvable, utilise les 20 derniers commits.

3. **Infère les changements de state** à partir de la conversation en cours et des commits — sans poser de questions :
   - Synthétise ce qui a été fait dans cette session (features livrées, tâches terminées, éléments bloqués)
   - Croise avec le git log pour confirmer ce qui est committé
   - Met à jour `state.md` directement avec ces observations

4. **Pose des questions uniquement pour les ambiguïtés non déductibles** :
   - Une décision d'archi ou une règle métier a-t-elle changé ? (si pas évident depuis les commits)
   - Un changement de pricing, rôles, ou onboarding client ? (si non visible dans le code)
   - Ne pose pas de question si la réponse est déjà dans la conversation ou les commits

5. **Mets à jour uniquement les sections concernées** dans les fichiers pertinents :
   - Changement de feature ou avancement → `state.md`
   - Nouvelle décision technique → `decisions.md`
   - Changement pricing/rôles → `business.md`
   - Changement architecture (nouvelle couche, nouveau service, nouveau flux) → `architecture.md`
   - Nouvelle table, modification de schéma, changement de conventions → `data-model.md`
   - Changement onboarding/billing → `clients.md`
   - Nouveau fichier mémoire créé → ajouter une ligne dans `MEMORY.md`

5. **Mets à jour la date** `_Dernière mise à jour_` dans chaque fichier modifié.

6. **Compresse chaque fichier modifié** avec caveman-compress pour garder les fichiers denses :
   - Invoque le skill `/caveman-compress` sur chaque fichier mis à jour
   - Ne compresse pas les fichiers non modifiés

## Règles

- Tu as les droits d'écriture complets sur tous les fichiers `.claude/memory/*.md` — écris directement sans demander confirmation
- Ne réécris pas ce qui n'a pas changé
- Reste concis — chaque ligne doit valoir son coût en tokens
- Si l'utilisateur ne répond pas à une question, laisse la section inchangée
- Ne crée jamais de nouveaux fichiers mémoire sans demander
