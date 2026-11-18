# Revue de l'étape 2 (faux consensus) par le groupe C

| | |
|---|---|
| Partie revue | Étape 2 : structure du code des scripts d'analyse, et cause commune des 0 |
| Auteurs | Groupe B [2] : Roy WEHBE, Enzo SIERRA-GUISSET, Florent SEYDOUX |
| Relecteurs | Groupe C [3] : Kuresa RAMEN, Paul CHARMOILLE, Thomas ANQUETIN |
| Corrections | commit [`71bde99`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/71bde996368bbaa489624bc1577bf187871ef185) |
| Autre revue de cette étape | [revue du groupe A](revue-A-etape2.md) : elle traite le choix des cas (C09 manqué) et le contrôle non vide. Nous ne les reprenons pas ici. |

## Résumé

Les résultats de l'étape 2 sont reproductibles : nous avons relancé le script et obtenu la même sortie.
Notre revue porte sur deux autres sujets : le **code copié d'un script à l'autre**, qui a déjà causé une
erreur réelle, et une **cause des faux 0** située dans le prompt, et non dans les modèles.

## Point 1 : la même logique était recopiée dans plusieurs scripts (maintenabilité, risque de divergence)

- **Où** : `explain_wrong_consensus.py`, `family_evidence.py`, `test_vote.py`, `check_prompts.py`.
- **Problème** : chaque script avait sa propre copie de trois choses :
  - **le chargement du skeleton et du vote** : 4 copies du même bloc `importlib` ;
  - **la conversion d'une ligne de trace en proposition de vote** (quels verdicts votent, `None` si pas de
    valeur) : 3 copies, légèrement différentes. L'une testait `r["value"] != ""`, une autre
    `r["value"]` ; `family_evidence.py` **devinait** le fournisseur avec `PROVIDER.get(m, "groq")` au lieu
    de le lire dans la trace ;
  - **la lecture de `reference-td1.csv`** : 2 copies, à la main.
- **Preuve que ce n'est pas théorique** : en écrivant `family_evidence.py`, la lecture recopiée des
  références a supposé une colonne `value`. Le script s'est arrêté sur `KeyError: 'value'`, car la colonne
  s'appelle `revenue_cents`. L'erreur a été vue et corrigée à la main dans ce seul script. Les autres copies
  restaient libres de diverger.
- **Pourquoi c'est problématique** : changer la règle « qui vote » (par exemple compter un `sql_rejected`
  comme indisponible) demandait de modifier 3 fichiers sans en oublier un. Un oubli donnerait des tables de
  vote différentes selon le script, toutes présentées comme « le vote du groupe ».
- **Amélioration faite** : [`td2/common.py`](../common.py) est désormais le seul endroit pour `load_vote()`,
  `proposal_from_row()` (le fournisseur est lu dans la trace) et `reference_values()`, qui passe par le
  chargeur du skeleton `load_references`, celui-là même qui note les traces. Les quatre scripts l'utilisent.
  Toutes les sorties régénérées sont **identiques** octet pour octet.

## Point 2 : la moitié des faux consensus vient d'une consigne du prompt (non corrigé, proposé pour le TD 3)

- **Constat** : sur les 4 valeurs fausses partagées, **3 valent 0** (C02, C09, C11, voir
  [`shared-errors.md`](../B-consensus/results/shared-errors.md)). Le prompt impose : « When no order line
  matches, return 0 (use COALESCE) » ([`prompts-en.md`](../../td1/prompts-en.md)). Un filtre faux ne produit
  donc pas d'erreur visible : il produit un 0 bien formé, qui vote comme une vraie valeur.
- **Hypothèse** (non mesurée) : sans cette consigne, ces requêtes renverraient `NULL`. Le bac à sable les
  classerait alors à part, et elles ne pourraient pas former un consensus sur 0.
- **Amélioration proposée** : demander une deuxième colonne `matched_lines` (`COUNT(*)`). Un 0 avec 0 ligne
  serait marqué « population vide » au lieu de voter. Ce n'est **pas appliqué** : le prompt doit rester
  identique pour que les traces du TD 1 restent comparables, et le TD 2 ne fait aucun nouvel appel. À
  tester au TD 3 sur un nouveau lot, avec un prompt daté et versionné.

## Ce qui est bien fait

- Les cas mêlant plusieurs runs sont signalés comme des illustrations (WC-3), ce qui évite de les compter
  comme des mesures.
- Le script ne modifie aucune donnée : SQL en lecture seule par le bac à sable du kit.

## Aurait-on pu faire mieux ?

Oui. Dès le deuxième script qui avait besoin du vote, il fallait créer le module commun plutôt que copier
le bloc. Le `KeyError` sur `revenue_cents` était le signal : la copie avait déjà dérivé.
