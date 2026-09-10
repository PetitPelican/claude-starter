# Avant d'affirmer

Onze questions, rejouées au moment où tu t'apprêtes à dire quelque chose qui
coûtera une décision à Maxime. Pas avant chaque tour : avant chaque **constat**.

Les sept premières valent partout. **Les quatre dernières sont ce que cinquante
notes de mémoire disent une fois qu'on les a compilées** — les mêmes quatre
pièges, sur ce poste, encore et encore.

## Partout

- **Ton instrument a-t-il répondu à LA question posée, ou à une plus petite ?**
  « ça marche ICI » ne répond pas à « ça marche LÀ-BAS ». Vingt-trois fois.
  **Et quand tu construis l'instrument toi-même : par combien de chemins la
  chose arrive-t-elle, et combien en vois-tu ?** Ce qu'un compteur ne voit pas
  passe pour inexistant — dis-le DANS le rapport, sinon le chiffre a l'air
  juste. **Mais COMPTE les chemins, ne les suppose pas** : le 09/09 j'ai annoncé
  qu'un compteur ne voyait « qu'une porte sur deux », puis mesuré qu'il n'y en
  avait qu'une. Un plancher annoncé sans preuve est une erreur au même titre
  qu'un total annoncé sans preuve — il a juste l'air prudent.
- **Le chiffre que tu lis mesure-t-il ce que tu crois ?** `unused` n'est pas la
  mémoire libre ; un cache n'est pas le service ; un dépôt n'est pas l'arbre
  qu'une commande a lu.
- **Ton contrôle est-il écrit dans le MÊME SENS que ton constat — et
  teste-t-il ce que le constat AFFIRME ?** Une ligne qui dit « ça manque » et
  une vérification qui demande « est-ce là » rendent TOMBÉ tant que le travail
  reste à faire. **Et une vérification épinglée sur un CHIFFRE EXACT tombe au
  premier enregistrement de qui que ce soit — le tien compris** : le 10/09 j'ai
  fait tomber mon propre constat en enregistrant chez les projets dont il
  parlait, et il exigeait « six ». Le chiffre est un décor, la revendication est
  « il en reste » : vérifie ça, jamais le décor. C'est la règle du bas — *l'as-tu
  périmé toi-même en travaillant ?* — et c'est la forme qui l'attrape le plus
  souvent.
- **Un tube n'a-t-il pas avalé le code de sortie de ce qui t'intéressait ?**
  `cmd --exit-status | tail` rend le succès de `tail`. Le pire est
  `| grep motif | tail` : l'échec de `grep` EST l'information.
- **« Rien vu » : vérifié bon, vérifié mauvais, ou pas mesuré ?** Les trois se
  ressemblent en sortie et ne veulent pas dire la même chose.
- **« Envoyé » n'est pas « arrivé ».** As-tu la preuve du côté qui reçoit ?
- **Ce fait, l'as-tu périmé toi-même en travaillant ?** L'âge n'est pas le seul
  déclencheur : « je viens de changer ce dont ce fait parle » en est un.

## Sur cette machine

- **Comptes et jetons — lis-tu l'état du compte, ou un cache ?** Un jeton vit
  dans une session de sécurité : **il n'existe aucun fichier à vérifier**, et
  429, jeton expiré et compte déconnecté se ressemblent en sortie. Seul un
  démarrage réel tranche. Et il n'y a **qu'un compte, sur le profil par
  défaut** — une connexion sans précaution l'écrase, retirer un profil rend
  invisibles les agents qui y tournent, et rien ne le dit.
- **Droits — as-tu LU ce droit, ou l'as-tu FRANCHI ?** Une déclaration dans un
  fichier de réglages ne dit rien de ce qui s'exécute : l'arbre en service peut
  porter une autre version. Un refus gagne partout et **ne se creuse pas**. Une
  API peut répondre 204 sans rien changer. Le seul contrôle est de faire le
  geste et de relire après.
- **Chemins — de quel arbre parle ta mesure, et lequel la session lit-elle ?**
  Plusieurs copies du même dépôt portent les mêmes noms de fichiers, et deux
  chiffres faux le même jour en sont sortis. Et **un nom est une adresse avant
  d'être un titre** : cinq points du poste rangent par chemin, un renommage
  déplace en silence ce qui s'y trouve.
- **Mécanismes — celui-ci a-t-il un appelant, et son déclencheur se produit-il
  vraiment ?** Une étiquette que l'agent doit poser lui-même ne se pose jamais
  — `échoué` existe depuis le début du carnet, zéro entrée sur vingt la porte.
  Un garde armé sur **l'action** au lieu du **résultat** se tait pour toujours
  après un seul passage. Et un témoin doit avoir **la même durée de vie que ce
  qu'il protège** : un compteur de session rangé dans un fichier d'agent se
  remplit une fois, définitivement.

<!-- ÉCRITURE — ce qui suit n'est pas servi à la lecture, c'est la règle du
     fichier lui-même. Il est court par construction : au-delà d'une dizaine de
     lignes, personne ne le lit, et il cesse d'être une liste de contrôle pour
     devenir un document de plus.

     LE PLAFOND EST DE ONZE — sept partout, quatre sur cette machine. Il n'est
     pas rond par hasard : c'est ce qui tient sous les yeux d'un coup. Ajouter
     une douzième ligne, c'est en CORRIGER une autre dans le même geste, ou
     n'ajouter rien.

     LA SECONDE SECTION EST UNE COMPILATION, pas un journal. Elle vient des
     notes de mémoire (`~/.claude/projects/<projet>/memory/`), qui restent la
     chronologie : elles gardent les cas, une par une, avec leurs dates. Ici on
     ne garde que ce qu'elles disent EN COMMUN — quatre familles pour une
     cinquantaine de notes. Un cas isolé n'y monte pas ; il y monte quand un
     TROISIÈME cas le rejoint, et alors on réécrit la ligne, on n'en ajoute pas.

     IL SE CORRIGE SUR PLACE, IL NE S'EMPILE PAS. La même leçon apprise deux
     fois est UNE règle : renforce-la ou précise-la, n'en ajoute pas une seconde
     copie, et n'écris jamais « MISE À JOUR : en fait… » en dessous — corrige la
     phrase qui a induit en erreur. C'est l'inverse du carnet d'équipe, qui reste
     en ajout seul parce que c'est une trace datée. Les deux sont tranchés
     différemment, exprès.

     CE QU'ON N'Y MET JAMAIS :
     · les pannes liées à l'environnement d'un jour — un réseau lent, un service
       en limitation de débit, un jeton expiré ;
     · et surtout AUCUNE AFFIRMATION NÉGATIVE SUR UN OUTIL. « X ne marche pas »,
       « on ne peut pas faire Y » durcissent en refus qu'on s'oppose à soi-même
       pendant des mois après que le problème a été réparé. Une liste de
       superstitions est pire que pas de liste.
     · rien qui ne soit pas rejouable par une question. Une anecdote n'est pas
       un contrôle.
-->
