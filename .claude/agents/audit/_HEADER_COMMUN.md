# Instructions communes à toutes les sessions d'audit

Colle ces instructions EN TÊTE de chaque prompt de session, avant le contenu spécifique.

---

## Contexte projet

Tu audites le monorepo de ce projet. Adapte les patterns ci-dessous à la stack détectée (framework web, framework mobile si applicable, ORM/client DB, provider de paiements).

**Règle absolue : ne modifie aucun fichier. Rapport uniquement.**

## Cartographie — à faire UNE SEULE FOIS au début de chaque session

```bash
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.sql" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.next/*" \
  -not -path "*/.expo/*" \
  -not -path "*/dist/*" \
  -not -path "*/.turbo/*" \
  -not -path "*/generated/*"
```

Lis **chaque fichier listé** intégralement. Ne saute aucun fichier, même court.

## Règles de discipline pendant l'audit

1. **Prends des notes intermédiaires après chaque fichier lu** — ne garde pas tout en mémoire de travail.
2. **Ne génère le rapport final qu'une fois tous les fichiers lus** — pas de rapport partiel.
3. **Si tu approches de ta limite de contexte : ARRÊTE-TOI.** Indique exactement le dernier fichier traité et ce qu'il reste à faire. Ne résume pas, ne compresses pas, ne sautes pas — arrête et signale.
4. **Si une section est propre : écris explicitement "Aucune occurrence détectée"** — ne saute pas la section.
5. **Numéro de ligne exact** pour chaque occurrence trouvée.
6. **Fichiers auto-générés** (types générés, lock files, dossiers de build) : note "ignoré — auto-généré" et passe au suivant.
7. **Si tu n'es pas certain** qu'une occurrence est problématique : inclus-la avec la mention `(à confirmer)`.
