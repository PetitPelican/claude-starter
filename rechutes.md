# Avant d'affirmer

Sept questions, rejouées au moment où tu t'apprêtes à dire quelque chose qui
coûtera une décision à Maxime. Pas avant chaque tour : avant chaque **constat**.

- **Ton instrument a-t-il répondu à LA question posée, ou à une plus petite ?**
  « ça marche ICI » ne répond pas à « ça marche LÀ-BAS ». Vingt-trois fois.
  **Et quand tu construis l'instrument toi-même : par combien de chemins la
  chose arrive-t-elle, et combien en vois-tu ?** Un compteur qui n'observe
  qu'une des deux portes rend un plancher, jamais un total — et ce qu'il ne voit
  pas passe pour inexistant. Dis-le DANS le rapport, sinon le chiffre a l'air
  juste.
- **Le chiffre que tu lis mesure-t-il ce que tu crois ?** `unused` n'est pas la
  mémoire libre ; un cache n'est pas le service ; un dépôt n'est pas l'arbre
  qu'une commande a lu.
- **Ton contrôle est-il écrit dans le MÊME SENS que ton constat ?** Une ligne
  qui dit « ça manque » et une vérification qui demande « est-ce là » rendent
  TOMBÉ tant que le travail reste à faire.
- **Un tube n'a-t-il pas avalé le code de sortie de ce qui t'intéressait ?**
  `cmd --exit-status | tail` rend le succès de `tail`. Le pire est
  `| grep motif | tail` : l'échec de `grep` EST l'information.
- **« Rien vu » : vérifié bon, vérifié mauvais, ou pas mesuré ?** Les trois se
  ressemblent en sortie et ne veulent pas dire la même chose.
- **« Envoyé » n'est pas « arrivé ».** As-tu la preuve du côté qui reçoit ?
- **Ce fait, l'as-tu périmé toi-même en travaillant ?** L'âge n'est pas le seul
  déclencheur : « je viens de changer ce dont ce fait parle » en est un.

<!-- ÉCRITURE — ce qui suit n'est pas servi à la lecture, c'est la règle du
     fichier lui-même. Il est court par construction : au-delà d'une dizaine de
     lignes, personne ne le lit, et il cesse d'être une liste de contrôle pour
     devenir un document de plus.

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
