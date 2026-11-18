<!-- Copie générée par td2/reviews/sync_copies.py depuis td2/reviews/revue-B-etape3.md. Ne pas modifier ici. -->
# Revue de l'étape 3 (routage) par le groupe B

| | |
|---|---|
| Partie revue | Étape 3 : coûts et paramètres du simulateur [`atelier-routage-grp2.py`](../../C-routing/atelier-routage-grp2.py), chemins des scripts, réalisme des contrôles |
| Auteurs | Groupe C [3] : Kuresa RAMEN, Paul CHARMOILLE, Thomas ANQUETIN |
| Relecteurs | Groupe B [2] : Roy WEHBE, Enzo SIERRA-GUISSET, Florent SEYDOUX |
| Corrections | commit [`25be186`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/25be186a5a40d819d1103d8a31e1dcb8b6aa757a) |
| Autre revue de cette étape | [revue du groupe A](revue-A-etape3.md) : elle traite l'éligibilité des modèles et le quorum. Nous ne les reprenons pas ici. |

## Résumé

Le coût de 0,000134 USD par requête est juste, et bien mieux fondé que le 0,30 fictif du kit. Mais les
nombres qui le produisent étaient **recopiés à la main**, comme les chemins des fichiers dans tous les
scripts. Deux contrôles de la règle sont aussi irréalistes au regard des délais annoncés.

## Point 1 : tokens et latences recopiés à la main

- **Où** : `TOKENS = {"gpt-oss-20b": (641, 286), ...}` et la colonne `latency_ms` de chaque ressource.
- **Problème** : ces moyennes avaient été calculées une fois dans un terminal, puis collées dans le code. Un
  nouveau run (prévu au TD 3) les aurait rendues fausses sans aucun signal, et le coût par requête avec elles.
- **Amélioration faite** : le simulateur mesure au démarrage les tokens et la latence moyens des réponses
  réussies du lot de base, dans `td1/traces-td1.csv`. Seuls les **prix** restent écrits dans le code,
  avec leur date et leur source (Groq, 5 octobre 2026), parce qu'ils ne viennent pas des traces. Valeurs
  mesurées identiques aux valeurs recopiées (une latence diffère d'1 ms) : sorties inchangées.

## Point 2 : chemins codés en dur dans chaque script

- **Où** : `ROOT / "td1" / "traces-td1.csv"` et variantes, répétés dans 8 scripts.
- **Preuve** : quand les livrables du TD 1 ont été rangés dans `td1/`, il a fallu modifier **9 fichiers** de
  `td2/` (scripts et sorties), en plus des liens des documents. Un seul chemin oublié aurait cassé un script qu'on ne relance pas
  souvent.
- **Amélioration faite** : [`common.py`](../../common.py) nomme une seule fois les entrées du TD 1
  (`TRACES_ALL`, `TRACES_BASE`, `TRACES_FULL1`, `REFERENCE`), et les 8 scripts utilisent ces noms. Un
  prochain déplacement ne touchera que ces quatre lignes.

## Point 3 : deux contrôles impossibles à tenir dans les délais (non corrigé, à trancher au TD 3)

- **Référence en 5 minutes** : pour « âge à la commande » et les combinaisons montrées au client, la règle
  exige une « independent reference query by a member », avec un délai de 5 minutes (scénario `urgent`). Un
  membre ne peut pas écrire et vérifier une requête indépendante en 5 minutes pour une question nouvelle.
  En pratique, ce contrôle n'existe que pour les 20 questions déjà référencées. Il faudra soit des requêtes
  de référence préparées par famille (modèles de requêtes vérifiés), soit **s'abstenir** quand la question
  sort de ces modèles.
- **Budget de 0,01 USD** : il est choisi sans justification. Il est 75 fois supérieur au coût mesuré d'une
  requête sur gpt-oss-20b, donc il n'est jamais contraignant, sauf dans le scénario où il vaut 0. Il
  devrait découler du coût d'une erreur pour l'usage concerné, qui est justement l'objet du TD 3.
- **Pourquoi nous ne l'avons pas corrigé** : ces choix demandent une décision du groupe (quel coût
  d'erreur, quelles familles préparer), pas une correction de code.

## Ce qui est bien fait

- Le coût vient de tokens réels multipliés par un prix daté de la même route, comme le décrit
  `methode-cout-en.md`.
- Le simulateur adapté garde l'interface du kit (`RESOURCES`, `choose`, `--scenario`). On compare donc les
  deux versions scénario par scénario.

## Aurait-on pu faire mieux ?

Oui : ne jamais coller dans le code un nombre qu'on peut recalculer depuis les traces. C'est la même leçon
que les chemins : un nombre ou un chemin écrit à un seul endroit ne peut pas diverger.
