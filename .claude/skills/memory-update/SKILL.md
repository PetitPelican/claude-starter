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

3. **Pose 3 questions ciblées à l'utilisateur** basées sur ce que tu observes dans les commits :
   - Qu'est-ce qui est maintenant terminé / en prod ?
   - Qu'est-ce qui est en cours ou bloqué ?
   - Y a-t-il une décision d'archi ou une règle métier qui a changé ?

4. **Mets à jour uniquement les sections concernées** dans les fichiers pertinents :
   - Changement de feature → `state.md`
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

- Ne réécris pas ce qui n'a pas changé
- Reste concis — chaque ligne doit valoir son coût en tokens
- Si l'utilisateur ne répond pas à une question, laisse la section inchangée
- Ne crée jamais de nouveaux fichiers mémoire sans demander
