<!-- Copie générée par td2/reviews/sync_copies.py depuis td2/reviews/revue-B-etape1.md. Ne pas modifier ici. -->
# Revue de l'étape 1 (quorum) par le groupe B

| | |
|---|---|
| Partie revue | Étape 1, le vote k-sur-n : `Orchestrateur.vote_k_sur_n` dans [`skeleton-multi-llm-en.py`](../../../skeleton-multi-llm-en.py), tests [`test_vote.py`](../../A-quorum/test_vote.py) |
| Auteurs | Groupe A [1] : Jason ZOH, Yohan ALLOUCHE |
| Relecteurs | Groupe B [2] : Roy WEHBE, Enzo SIERRA-GUISSET, Florent SEYDOUX |
| Corrections | commit [`0103770`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/01037707e8240f7a8859d8d5482ed46e1275b717) |
| Autre revue de cette étape | [revue du groupe C](revue-C-etape1.md) : elle traite le pilote `run_vote.py` et les retry. Nous ne les reprenons pas ici. |

## Résumé

La méthode respecte les cinq règles du contrat de l'énoncé, et ses 16 tests passent. Nous avons relevé trois
faiblesses, toutes dans la **méthode de vote elle-même** et dans **ses tests**. Aucune ne change les tables
de décisions du TD 2, mais chacune peut produire un résultat faux sans message d'erreur dans un autre usage.

## Point 1 : un verdict inconnu était ignoré en silence (bug, sévérité moyenne)

- **Où** : boucle de la règle 1 de `vote_k_sur_n`.
- **Problème** : la méthode ne comptait une voix que si `verdict == "executed"`, et traitait **toute autre
  valeur** comme une erreur. Or les traces du skeleton n'utilisent jamais `executed` : leurs verdicts sont
  `correct`, `incorrect`, `sql_invalid`, etc.
- **Scénario d'échec** : quelqu'un passe directement des lignes de `traces-td1.csv` au vote, sans passer par
  `atelier-vote.py`. Les trois membres ont alors le verdict `correct` et la même valeur, mais la méthode
  renvoyait `{"consensus": false, "votes": 0}`. On obtenait une abstention qui ressemble à un vrai désaccord.
  L'erreur passe inaperçue : une abstention est une sortie normale du vote.
- **Amélioration faite** : un verdict autre que `executed` ou `error` lève maintenant un `ValueError`, avec un
  message qui dit quoi faire (« convert trace rows into proposals before voting »). Nouveau test **T17**.

## Point 2 : deux modèles d'une même famille comptaient pour deux voix (écart au CM2)

- **Où** : règle 3 (refus des doublons).
- **Problème** : le contrat de l'énoncé ne refuse que le même couple (fournisseur, modèle). Le CM2 va plus
  loin : « deux accès à la même famille comptent pour une seule voix ». Avec le panel
  {gpt-oss-120b, gpt-oss-20b, qwen3.8-27b}, les deux modèles OpenAI pouvaient former à eux seuls un
  « consensus » 2 sur 3. Nous l'avons vérifié : le test **T19** renvoie bien un consensus sur cette paire.
- **Pourquoi c'est problématique** : deux modèles d'une même famille partagent leurs habitudes d'erreur.
  C'est précisément ce que le quorum est censé éviter. Dans nos traces, gpt-oss-20b et gpt-oss-120b sont les
  seuls justes sur C10 et sur les combinaisons : un panel qui les contient tous les deux masquerait le fait
  qu'une seule famille sait répondre.
- **Amélioration faite** : une option `distinct_families=True` refuse un panel où une famille apparaît deux
  fois (famille = préfixe fournisseur du `model_requested`, par exemple `openai`). Test **T18**. Nous l'avons
  laissée optionnelle pour ne pas casser le contrat de l'énoncé, que `atelier-vote.py` appelle sans option.
- **Limite** : le préfixe est une approximation de la famille. Deux fournisseurs pourraient servir des
  modèles dérivés d'une même base.

## Point 3 : les tests ne vérifiaient pas quels modèles étaient d'accord

- **Où** : `test_vote.py`, comparaison `result[key] == val` limitée aux clés de `expected`.
- **Problème** : les cas attendus ne contenaient que `consensus`, `value` et `votes`. Une méthode qui
  renverrait la bonne valeur mais une liste `models` fausse (le mauvais membre, ou un membre indisponible)
  passait tous les tests. Or cette liste est ce qui permet de savoir *qui* a fait le consensus (dans WC-1,
  c'est elle qui montre que 20b et north sont d'accord sur 0).
- **Amélioration faite** : les six cas de consensus vérifient maintenant la liste exacte des modèles, dans
  l'ordre du panel. Les tests passent de 16/16 à **19/19**
  ([`voting-tests-en.csv`](../../A-quorum/voting-tests-en.csv), [`test-vote.txt`](../../A-quorum/results/test-vote.txt)).

## Ce qui est bien fait

- n compte tous les membres, y compris ceux qui ne votent pas ; k est contrôlé (`n // 2 < k <= n`).
- La valeur 0 est bien une voix et non une absence de valeur (T16). La méthode ne connaît pas la référence.
- Un booléen n'est pas accepté comme entier (`isinstance(value, bool)`), ce qui évite que `True` vaille 1 centime.

## Aurait-on pu faire mieux ?

Oui, sur la manière de tester : écrire les tests **avant** la méthode, à partir des cinq règles. Le point 1
serait alors apparu tout de suite, avec la question « que fait la méthode d'un verdict qu'elle ne
connaît pas ? ».
