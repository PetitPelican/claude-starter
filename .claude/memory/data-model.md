# Modélisation des données — [PROJECT_NAME]
_Dernière mise à jour : YYYY-MM-DD_

## Couches

<!-- Adapter selon le projet : supprimer les couches non utilisées -->
<!-- Exemple data warehouse : raw → staging → intermediate → marts -->
<!-- Exemple SaaS : public schema PostgreSQL uniquement -->

### Raw / Bronze
_Données brutes, jamais transformées. Fidèles à la source._

| Table | Source | Colonnes clés | Notes |
|---|---|---|---|
| | | | |

### Staging / Silver
_Données nettoyées, typées, dédupliquées. Pas de logique métier._

| Table | Depuis | Colonnes clés | Notes |
|---|---|---|---|
| | | | |

### Intermediate
_Agrégations intermédiaires, jointures complexes. Usage interne uniquement._

| Table / Vue | Dépend de | Colonnes clés | Notes |
|---|---|---|---|
| | | | |

### Marts / Gold
_Tables exposées aux utilisateurs finaux (BI, API, frontend)._

| Table | Exposée à | Colonnes clés | Notes |
|---|---|---|---|
| | | | |

---

## Relations clés

```
[TABLE_A] --< [TABLE_B]   (one-to-many)
[TABLE_C] >--< [TABLE_D]  (many-to-many via [TABLE_E])
```

---

## Conventions

- Nommage : [À compléter — ex: snake_case, préfixe par couche stg_ / fct_ / dim_]
- Clés primaires : [À compléter — ex: UUID, integer auto-increment]
- Timestamps : [À compléter — ex: created_at / updated_at sur toutes les tables]
- Soft delete : [oui / non]
