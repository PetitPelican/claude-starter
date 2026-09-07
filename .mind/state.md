---
maj: 2026-09-07
sante: vert
jalon: [LE_PROCHAIN_CAILLOU — celui qui débloque les autres]
---

# État — [PROJECT_NAME]

> Répond à **« où on en est ? »**. **Public** — alimente la section « Suivi » du
> site de doc. Le journal figé des choix est dans `docs/decisions.md` ; les
> tâches sont dans `todo.md`, à côté.

**L'en-tête ci-dessus est lu par la machine.** `mind-guard` refuse un commit
s'il est absent ou mal formé, et le tableau de bord range alors le projet en
« aucune déclaration » : il en disparaît **sans bruit**. Quatre règles :

- `maj:` est une date ISO `AAAA-MM-JJ`, et c'est **celle du jour où on écrit**.
- `cap:` et `jalon:` ne sont jamais vides. Sans cap, personne ne sait où va le
  projet ; sans jalon, personne ne sait ce qui bloque.
- `sante:` vaut `vert`, `orange` ou `rouge`. C'est la santé **déclarée** par
  l'agent — à ne pas confondre avec une mesure machine.
- Ce fichier est un **instantané roulant borné**, pas un journal. Le texte
  périmé s'y **remplace** ; ce qui mérite d'être gardé daté va dans
  `docs/decisions.md`.

## Phase

[À remplir — où on en est vraiment, en une phrase lisible par quelqu'un qui n'a
pas ouvert le dépôt. Ex : « Étude. Aucun engagement pris, aucune date imposée. »]

## Ce qui tient

- _(à remplir — ce qui est fait **et vérifié**. « Vérifié » veut dire mesuré,
  pas supposé.)_

## Ce qui ne tient pas

- _(à remplir — ce qui est cassé, incertain, ou **pas encore mesuré**. Ne rien
  voir n'est pas un succès : un point non mesuré va ici, jamais au-dessus.)_
