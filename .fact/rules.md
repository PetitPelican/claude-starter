# Règles de gestion & contraintes — [PROJECT_NAME]

> Répond à **« quelles règles gouvernent le projet ? »**. **Public** — sert de
> base à la page « Règles de gestion » du site de doc.

**Chaque règle porte la panne qu'elle évite.** Une règle sans son pourquoi se
fait contourner à la première gêne — et celui qui la contourne a raison, faute
de savoir ce qu'elle protégeait.

## Les invariants du harnais — arrêtés le 04/09/2026

_Ceux-là ne sont pas à remplir : ils valent pour tout projet du starter, et
chacun porte la panne mesurée qui l'a fait écrire._

- **`.fact/` est fermé à quatre fichiers** — `base`, `architecture`, `stack`,
  `rules`. Un cinquième est une erreur, pas une extension : c'est la garde qui
  a tenu cinq mois pour `.mind/`.
- **`.mind/` n'en porte que deux** — `state`, `todo` — et il y en a **un jeu par
  agent** : à la racine en mono-agent, dans `agents/<nom>/` dès qu'il y en a
  plusieurs. Jamais de `.mind/` à la racine d'un projet multi-agents : personne
  n'y travaillerait pour le tenir.
- **Ce qui est caché est du harnais, ce qui est visible est pour le commanditaire.**
  `.fact/`, `.mind/`, `.logs/` sont pointés ; `docs/` ne l'est pas. Cette
  mémoire ne sert pas d'abord à l'agent.
- **`docs/` ne contient que de l'écrit à la main.** Toute sortie de build va
  ailleurs (`site/` pour le site rendu). Sans cette règle, on ne distingue plus
  la vérité tenue à la main de ce qui se régénère.
- **`.fact/` ne s'écrit qu'à la demande du commanditaire.** `mind-guard` refuse un
  commit qui y touche sans ` # fact-ok` en fin de commande. Raison : c'est la
  seule mémoire partagée par tous les agents, et un agent qui la réécrit depuis
  son lot efface le travail d'un autre sans que personne ne le voie.
- **En multi-agents, `<projet>/.claude/settings.json` ne s'exécute pas.**
  Mesuré : les réglages ne s'héritent pas, seul celui du dossier de lancement
  compte. La racine ne garde que `hooks/`, appelés par les agents en
  `../../.claude/hooks/…`. Y poser un `settings.json` produirait un fichier que
  quelqu'un éditera un jour en croyant agir sur tous les agents.
- **En mono-agent, l'appel reste `.claude/hooks/…`.** L'agent EST à la racine :
  `../../` y désignerait `~/.claude/hooks/`, qui n'existe pas — et un hook
  absent ne dit rien, il ne tourne pas, en silence.
- **Un `deny` s'écrit en chemin ancré sur le home**, jamais en relatif. Mesuré
  le même jour : `Edit(../autre/**)` ne mord PAS (le fichier a été modifié
  malgré la règle), `Edit(~/Agentic/<Projet>/agents/<autre>/**)` mord, y compris
  en mode `bypassPermissions`. Et seules les règles `Edit(...)` sont évaluées :
  `Write(...)` est inerte.
- **Deux agents d'un même projet ne portent jamais des noms qui se slugifient
  pareil.** `<projet> OPS` et `<projet>-OPS` donnent la même adresse de mémoire
  auto : ce serait deux agents partageant une seule mémoire, en silence.
- **Aucune phrase du `CLAUDE.md` du projet n'est reprise dans celui d'un
  agent.** Le test : si elle resterait vraie pour un autre agent, elle est à
  l'étage au-dessus. Le `CLAUDE.md` du projet est chargé à chaque démarrage de
  chaque agent — une phrase répétée est payée deux fois par session.

## Règles métier

_Chaque règle du domaine, où elle est appliquée, et ce qui casse sans elle._

| Règle | Où / comment appliquée | Ce qu'elle évite |
|---|---|---|
| [à remplir] | [à remplir] | [à remplir] |

## Règles d'accès (RBAC / RLS)

_Qui a le droit de faire quoi. Le détail des rôles vit dans `architecture.md`,
section « Les frontières »._

- [à remplir — ex : chaque utilisateur ne voit que ses données ; vérifié côté
  serveur, jamais seulement côté client]

## Contraintes

- [à remplir — conformité (RGPD/SOC2), budget infra, SLA, exigences de sécurité
  de haut niveau]

## Ce qui n'est PAS une règle

_Les préférences, les habitudes, les « on fait plutôt comme ça ». Les écrire ici
les empêche de se durcir en interdits que personne n'a décidés._

- [à remplir]

<!-- Ne jamais écrire ici de secret, token, clé, ni d'IP/URL sensible :
     ça va dans docs/operations.md (privé). -->
