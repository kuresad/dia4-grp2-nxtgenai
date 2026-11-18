# Revue de l'étape 3 (routage) par le groupe A

| | |
|---|---|
| Partie revue | Étape 3 : critère d'éligibilité de [`routing-rule.md`](../C-routing/routing-rule.md) et du simulateur [`atelier-routage-grp2.py`](../C-routing/atelier-routage-grp2.py), contrôle par quorum |
| Auteurs | Groupe C [3] : Kuresa RAMEN, Paul CHARMOILLE, Thomas ANQUETIN |
| Relecteurs | Groupe A [1] : Jason ZOH, Yohan ALLOUCHE |
| Corrections | commit [`2e3b593`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/2e3b593353e02c4375fc51838cdf25e100ac9c8a) |
| Autre revue de cette étape | [revue du groupe B](revue-B-etape3.md) : elle traite les coûts, les chemins et les délais. Nous ne les reprenons pas ici. |

## Résumé

La règle suit bien l'ordre d'usage du CM2 et justifie chaque ligne par des cellules du TD 1. Notre revue
porte sur **la façon dont le simulateur sait quel modèle est capable de quoi**. Cette information était
recopiée à la main, reposait sur un seul run, et le contrôle par quorum comptait un membre qui ne peut pas
aider.

## Point 1 : les capacités des modèles étaient recopiées à la main dans le simulateur

- **Où** : `RESOURCES`, champs `families` (ensembles comme `SIMPLE | {"completed age at a date"}`) et
  `evidence` (texte libre comme « 16/20 in D-kuresa-1 ... »).
- **Problème** : ces valeurs viennent de [`family-evidence.md`](../C-routing/results/family-evidence.md),
  mais elles étaient **retapées**. Rien ne vérifiait que le simulateur et la preuve disent la même chose. Une
  nouvelle trace, ou une faute de frappe dans un ensemble, aurait changé les décisions sans que la règle
  écrite change.
- **Amélioration faite** : au démarrage, le simulateur calcule l'éligibilité de chaque modèle à partir de
  `td1/traces-td1.csv`, avec `family_scores()` du module commun. Le texte de preuve de chaque décision est
  généré à partir des mêmes chiffres, par exemple « gpt-oss-20b on completed age at a date: base 4/4 (B-1);
  other runs FULL-1 2/4 ». Les décisions par défaut sont **inchangées**, ce qui confirme que la saisie
  manuelle était juste. Elle ne peut simplement plus dériver.

## Point 2 : l'éligibilité reposait sur un seul run par modèle

- **Problème** : un modèle est éligible s'il est juste sur toute la famille **dans le lot de base**, soit un
  seul run. Or les répétitions du TD 1 montrent que les verdicts changent d'un run à l'autre, à prompt et
  température 0 identiques (voir [`pivot-td1.md`](../../td1/notes/pivot-td1.md), dernière table). La règle
  choisit gpt-oss-20b pour « âge à une date » (4/4 dans B-1), alors qu'il fait 2/4 dans FULL-1. qwen3.8-27b
  sert de membre du quorum sur cette famille, alors qu'il fait 2/4 dans D-paul-2.
- **Amélioration faite** : une option `--criterion every-run` exige que toutes les cellules soient justes
  dans **tous** les runs du modèle. Sortie : [`simulator-after-every-run.jsonl`](../C-routing/results/simulator-after-every-run.jsonl).
  Une seule décision change : la question d'âge destinée à un versement part sur **gpt-oss-120b** (4/4 dans
  ses 4 runs), et le contrôle devient une référence, parce que le quorum ne peut plus confirmer. Le critère
  par défaut reste celui de l'énoncé (« correct sur la famille dans la table du TD 1 »). L'autre critère
  montre ce qu'il coûte d'être plus prudent : 0,60 au lieu de 0,30 USD par million de tokens de sortie.
- **Limite** : 2 à 5 runs par modèle ne suffisent pas à estimer une stabilité. Le critère strict reste une
  hypothèse liée à ce lot.

## Point 3 : le contrôle par quorum comptait un membre inutile

- **Où** : `checks_for`, branche « 2-of-3 ».
- **Problème** : le simulateur affichait « panel available 3/3 » pour une question d'âge. Or north-mini-code
  fait **0/4** sur cette famille dans le lot de base. Sa voix ne peut pas confirmer une bonne valeur ; au
  mieux il se trompe seul. Le quorum réel n'était donc qu'un 2 sur 2 entre gpt-oss-120b et qwen, qui ne
  tolère aucune erreur. Le message « 3/3 » donnait une confiance que le panel n'a pas.
- **Amélioration faite** : seuls les membres **disponibles et éligibles** sur la famille comptent. La
  décision dit lesquels sont écartés (« not counted: north-mini-code:free ») et prévient quand il n'en reste
  que deux (« no failure tolerated »). S'il en reste moins de deux, le contrôle passe à la référence.

## Ce qui est bien fait

- Chaque ressource écartée l'est **nommément**, avec sa raison. Une personne extérieure au groupe peut
  auditer la décision, comme le demande le CM2.
- La règle distingue bien les familles où un quorum a un sens de celles où une seule famille de modèles sait
  répondre (C10, combinaisons).

## Aurait-on pu faire mieux ?

Oui. La table du TD 1 contenait déjà toutes les répétitions. Les utiliser dès l'écriture de la règle
aurait évité de baser l'éligibilité sur un run unique.
