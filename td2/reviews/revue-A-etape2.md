# Revue de l'étape 2 (faux consensus) par le groupe A

| | |
|---|---|
| Partie revue | Étape 2 : [`wrong-consensus.md`](../B-consensus/wrong-consensus.md), [`explain_wrong_consensus.py`](../B-consensus/explain_wrong_consensus.py) et sa sortie |
| Auteurs | Groupe B [2] : Roy WEHBE, Enzo SIERRA-GUISSET, Florent SEYDOUX |
| Relecteurs | Groupe A [1] : Jason ZOH, Yohan ALLOUCHE |
| Corrections | commit [`17d7258`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/17d7258ed9a1536cff2531127deef7fcccf85a24) |
| Autre revue de cette étape | [revue du groupe C](revue-C-etape2.md) : elle traite la structure du code (duplication) et le prompt. Nous ne les reprenons pas ici. |

## Résumé

Les trois cas présentés (C02, C10, C11) sont justes, et leurs causes SQL sont bien démontrées. Mais ils ont
été **choisis à la main**. Une recherche systématique trouve un quatrième cas, plus grave, qui contredit la
conclusion principale du document. Par ailleurs, le contrôle « population non vide » était affirmé, pas
exécuté.

## Point 1 : la recherche à la main a manqué le seul faux consensus du panel déclaré (sévérité haute)

- **Où** : `explain_wrong_consensus.py` code en dur C02, C11 et C10.
- **Problème** : personne n'a parcouru *toutes* les valeurs fausses partagées. Le document concluait :
  « le panel fixe ne renvoie aucun faux consensus ».
- **Preuve** : le nouveau script [`scan_shared_errors.py`](../B-consensus/scan_shared_errors.py)
  ([sortie](../B-consensus/results/shared-errors.md)) liste toutes les valeurs fausses renvoyées par au moins
  deux modèles. Il en trouve quatre, dont **C09 = 0, renvoyé par trois familles** (north-mini-code, qwen3.8-27b
  dans 3 de ses 5 runs, dots-3-note). Il vote aussi le panel fixe sur **les 40 combinaisons** d'un run par
  membre (4 × 2 × 5). Résultat sur C09 : 16 justes, **12 faux consensus**, 12 abstentions.
- **Pourquoi c'est important** : le « 0 faux consensus » du lot de base tient à la chance. Dans ce lot, qwen
  a eu juste sur C09 (`D-kuresa-1`), alors qu'il se trompe dans 3 runs sur 5. Avec un autre run de qwen, le
  panel déclaré lui-même se trompe.
- **Amélioration faite** : ajout du script de recherche, et cas **WC-4** dans
  [`wrong-consensus.md`](../B-consensus/wrong-consensus.md) avec la cause SQL : trois filtres différents,
  chacun contradictoire, donc vides, donc 0. qwen calcule de plus l'âge à la date de la *commande* au lieu de
  la date de référence. La conséquence n° 1 du document est corrigée.

## Point 2 : le contrôle « population non vide » était affirmé, pas mesuré

- **Où** : `explain_wrong_consensus.py`, ligne qui imprimait « all prices and quantities > 0, so 0 is
  impossible ».
- **Problème** : le script comptait les lignes en Python, puis **écrivait** que les prix et quantités sont
  positifs, sans le vérifier. Or c'est cette affirmation qui permet de réfuter le 0 : si une ligne avait un
  prix nul, un total de 0 deviendrait possible. Le contrôle indépendant mis en avant par l'étape 2 reposait
  donc sur une hypothèse.
- **Amélioration faite** : [`probes.py`](../B-consensus/probes.py) réexécute la requête de référence en
  lecture seule, avec `COUNT(*)` et `MIN(quantité × prix)` à la place de la somme. Pour C02 : 82 lignes, plus
  petite ligne 1 250 centimes. La section 3 de `shared-errors.md` applique cette sonde à **chaque** 0 faux
  des traces (C02, C08, C09, C10, C11, C15, C19) : elle les réfute tous, sans modèle.
- **Limite** : la sonde utilise la population de la *référence*. Elle prouve qu'un 0 est faux, mais ne
  remplace pas la référence pour une valeur non nulle (WC-3, 119 410).

## Ce qui est bien fait

- Chaque requête est **réexécutée** à partir des traces, et comparée à un recalcul Python indépendant, sans SQL.
- La nature de chaque cas est indiquée (lot réel, runs combinés, synthétique), et DEMO-VOTE est séparé des
  comptages, comme le demande l'énoncé.
- WC-3 décompose la valeur fausse (119 410 + 439 570 = 558 980). C'est la meilleure preuve de cause du
  document.

## Aurait-on pu faire mieux ?

Oui : commencer par la recherche systématique, puis choisir les cas à commenter. Avec 5 modèles, 11 runs et
20 questions, il y a trop de cellules pour une lecture à l'œil.
