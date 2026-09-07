# À faire — [PROJECT_NAME]

> Répond à **« qui doit bouger, et sur quoi ? »**. **Public** — alimente la
> section « Suivi » du site de doc, avec `state.md`.

**Ce fichier est lu par la machine.** Le tableau de bord en tire le kanban de
chaque projet et, surtout, **ce qui attend une décision humaine**. Le dialecte
n'est donc pas décoratif :

    - [ ] à faire        - [>] en cours        - [x] fait
    !haut · !moyen · !bas          @<qui> · @dehors

- **`@<qui>` est le marqueur le plus important du fichier.** Il nomme la
  personne — `@user`, un prénom, celui qu'on veut — dont la décision manque,
  et c'est ce qui remonte **en premier** dans tout point d'avancement, parce que
  c'est la seule chose qui ne se délègue pas.
  `@dehors` est le seul nom réservé : il marque ce qui attend un tiers hors de
  l'équipe — client, prestataire, administration — que personne ici ne peut
  lever.
- Une tâche s'écrit sur **une seule ligne**. Le parseur lit tout le fichier,
  section par section — un libellé qui déborde sur la ligne suivante est perdu.
- `mind-guard` refuse un commit si ce fichier ne contient plus **aucune tâche
  lisible**.

> ⚠️ **Ce fichier ne se compresse JAMAIS.** Toute compression fusionne les
> puces : `!haut` et `@<qui>` disparaîtraient sans bruit, et avec eux tout ce
> qui remonte à l'humain. Même règle pour les journaux `.logs/`, qui sont
> append-only par construction.

## Chantiers

- [ ] !haut @user [LA_PREMIÈRE_DÉCISION_QUI_BLOQUE]
- [ ] !moyen [LE_PREMIER_TRAVAIL_QUI_NE_DÉPEND_DE_PERSONNE]
- [ ] !bas [CE_QUI_PEUT_ATTENDRE]
