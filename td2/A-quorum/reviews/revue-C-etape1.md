<!-- Copie générée par td2/reviews/sync_copies.py depuis td2/reviews/revue-C-etape1.md. Ne pas modifier ici. -->
# Revue de l'étape 1 (quorum) par le groupe C

| | |
|---|---|
| Partie revue | Étape 1 : le pilote [`run_vote.py`](../../A-quorum/run_vote.py), les tables des 20 décisions, et les retry du TD 1 qui alimentent le vote |
| Auteurs | Groupe A [1] : Jason ZOH, Yohan ALLOUCHE |
| Relecteurs | Groupe C [3] : Kuresa RAMEN, Paul CHARMOILLE, Thomas ANQUETIN |
| Corrections | commit [`0a4c083`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/0a4c0832ab44cae9e4875beecc8016d9a48ac4df) |
| Autre revue de cette étape | [revue du groupe B](revue-B-etape1.md) : elle traite la méthode `vote_k_sur_n` et ses tests. Nous ne les reprenons pas ici. |

## Résumé

Les tables des 20 décisions sont justes pour les deux fichiers utilisés (le lot de base et FULL-1). Mais
le pilote **acceptait n'importe quel fichier**, et sur le fichier fusionné il produisait un faux consensus
sans le signaler. Nous expliquons aussi les retry du TD 1 : deux d'entre nous (Kuresa, Paul) ont lancé les
runs qwen qui les ont subis.

## Point 1 : un fichier qui mélange les runs produisait un faux consensus silencieux (bug, sévérité haute)

- **Où** : `run_vote.py`, qui appelle `atelier-vote.py --traces <fichier>`. L'atelier prend la *dernière
  ligne* de chaque membre du panel.
- **Problème** : l'énoncé montre la commande `--traces traces-td1.csv`. Or `td1/traces-td1.csv` contient
  11 runs fusionnés. La « dernière ligne » d'un membre vient alors d'un run différent pour chaque modèle. Le
  docstring de l'atelier dit « rejeter les expériences mélangées », mais rien ne le faisait.
- **Preuve** : sur `td1/traces-td1.csv`, avant correction, la sortie était
  `15 consensus (14 equal to the reference, 1 wrong)`. Le faux consensus est **C09 = 0** : north-mini-code
  vient de `C-jason-1` et qwen3.8-27b de `D-kuresa-2`, deux runs sans rapport. Le panel affiche alors un
  consensus que personne n'a jamais mesuré.
- **Amélioration faite** : le pilote refuse un fichier où un membre du panel a plusieurs `run_id` pour une
  même question, et liste les cellules en cause (`C01 gpt-oss-120b: A-jason-1 + A-jason-2 + ...`).
- **Reste à faire** : la même protection manque dans `atelier-vote.py`, qui est un fichier du kit et que
  nous n'avons pas modifié.

## Point 2 : « unavailable » cachait la vraie raison, et n était codé en dur

- **Où** : construction de la table dans `run_vote.py`.
- **Problème** : un membre sans voix était affiché `unavailable`, quelle que soit la cause. Dans FULL-1,
  north-mini-code n'est pas indisponible sur C09 : il a répondu un SQL invalide (`sql_invalid`). Un 429 non
  rattrapé et un SQL rejeté par le bac à sable ne demandent pas la même réaction. Le premier relève du
  routage (attendre ou changer de modèle), le second du prompt. Par ailleurs `"votes": "x/3"` et
  `20 - n_cons` supposaient toujours 3 membres et 20 questions.
- **Amélioration faite** : la table affiche le verdict de la dernière tentative, avec le statut HTTP s'il
  n'est pas 200 (par exemple `not_executed (HTTP 429)`). n et le nombre de questions sont calculés. Effet
  visible dans [`vote-full1.md`](../../A-quorum/results/vote-full1.md) : C09 affiche `sql_invalid`.

## Point 3 : les retry du TD 1, et ce qu'ils font au vote

Analyse générée par [`retry_analysis.py`](../../A-quorum/retry_analysis.py) →
[`results/retries.md`](../../A-quorum/results/retries.md).

- **Ce qui s'est passé** : 22 réponses HTTP 429. Une seule vient de gpt-oss-20b (quota de 8 000 tokens par
  minute dans B-1). Les 21 autres viennent de qwen3.8-27b, dans ses 4 runs sur le plan gratuit Groq, toujours
  à partir de C16. Le message de Groq donne la cause : *output tokens per minute (OTPM): Limit 1000*.
- **Pourquoi c'était prévisible** : le skeleton attend 3 s entre deux requêtes, ce qui fait environ 17
  requêtes par minute. qwen produit en moyenne 136 tokens par réponse, soit environ 2 300 tokens par minute :
  plus de deux fois le quota. Le quota se remplit en 15 questions environ, puis chaque question échoue une
  première fois. Pour rester sous 1 000, il aurait fallu environ 8 s entre deux requêtes.
- **Le retry** : le skeleton réessaie une seule fois après le délai `Retry-After`. 16 retry ont réussi
  (après 3 à 12 s), 3 ont reçu un second 429 (après 3 à 11 s). Le retry est donc parfois arrivé trop tôt.
  Résultat : `D-paul-2` C19, `D-kuresa-2` C17 et C20 sont restés `not_executed`.
- **Effet sur le vote** : dans le lot de base, tous les 429 ont été rattrapés. Les tables de l'étape 1 n'ont
  donc aucun membre rendu indisponible par le quota. Un vote sur `D-paul-2` ou `D-kuresa-2` aurait eu qwen
  absent sur ces questions : il reste dans n sans voter, et le panel ne tolère alors plus aucune erreur des
  deux autres membres.
- **Erreur du groupe** : 319 tentatives au lieu des 100 cellules prévues. Les répétitions qwen ont été
  lancées à la suite, chacune sur un compte personnel, avec la même pause de 3 s. Elles ont reproduit les
  mêmes 429 au lieu d'en tirer la leçon.
- **Amélioration** : l'analyse est faite et chiffrée. Pour le TD 3, si un nouveau run est nécessaire, la
  pause doit être calculée à partir du quota : `60 × tokens de sortie moyens / quota`, soit 8,2 s pour qwen.
  Nous n'avons pas modifié la pause du skeleton : l'énoncé du TD 2 demande de ne changer que `vote_k_sur_n`.

## Ce qui est bien fait

- Le pilote lance l'atelier **sans le modifier**, ligne par ligne, et garde la sortie JSON brute
  ([`vote-base.jsonl`](../../A-quorum/results/vote-base.jsonl)) à côté de la table.
- La référence n'est lue qu'après la décision, par l'atelier.

## Aurait-on pu faire mieux ?

Oui. Le docstring du pilote disait déjà qu'un fichier mélangé « ne doit pas être utilisé ». Une règle
écrite seulement dans un commentaire ne protège personne : il fallait la vérifier dans le code.
