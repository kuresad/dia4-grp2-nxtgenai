# Rapport du TD 2 : le quorum, puis la règle de routage

Sous-groupe DIA4 GRP2, séance du 18 novembre 2026, pack `2026-10-14-students-1`. **Aucun modèle n'a été appelé
au TD 2** : chaque chiffre ci-dessous rejoue hors ligne les traces stockées du TD 1 (`nature = real`), sauf les
simulations et le DEMO-VOTE synthétique, qui sont signalés comme tels. Les prompts n'ont pas changé
([`prompts-en.md`](../td1/prompts-en.md) ; 319/319 empreintes de traces concordent, [`td2/check-prompts.txt`](../td2/check-prompts.txt)).

## Ce qui a été tenté et réalisé

| Étape | Livrable | Fichier | Statut |
|---|---|---|---|
| 1 | `vote_k_sur_n` complétée | [`skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py) (`Orchestrateur.vote_k_sur_n`) | fait |
| 1 | Tests du contrat : accord, désaccord, membres indisponibles, route en double, k invalide, 3 sur 5, faux consensus | [`td2/A-quorum/test_vote.py`](../td2/A-quorum/test_vote.py) → [`voting-tests-en.csv`](../td2/A-quorum/voting-tests-en.csv), [`test-vote.txt`](../td2/A-quorum/results/test-vote.txt) | 19/19 passent (16 avant les revues croisées) |
| 1 | Pilote : `atelier-vote.py --traces … --case Cxx` sur les vingt questions | [`td2/A-quorum/run_vote.py`](../td2/A-quorum/run_vote.py) | fait |
| 1 | **Table des vingt décisions** (panel et k déclarés ci-dessous) | [`vote-base.md`](../td2/A-quorum/results/vote-base.md) (lot de base), [`vote-full1.md`](../td2/A-quorum/results/vote-full1.md) (run FULL-1) ; CSV et JSONL bruts à côté | fait |
| 2 | Faux consensus commenté | [`td2/B-consensus/wrong-consensus.md`](../td2/B-consensus/wrong-consensus.md), preuve [`explain-wrong-consensus.txt`](../td2/B-consensus/results/explain-wrong-consensus.txt) | fait |
| 3 | Règle de routage d'une page avec les cellules du TD 1 | [`td2/C-routing/routing-rule.md`](../td2/C-routing/routing-rule.md), preuve [`family-evidence.md`](../td2/C-routing/results/family-evidence.md) | fait |
| 3 | Sorties du simulateur avant et après adaptation | [`simulator-before.jsonl`](../td2/C-routing/results/simulator-before.jsonl) (`atelier-routage.py` du kit), [`simulator-after.jsonl`](../td2/C-routing/results/simulator-after.jsonl) ([`atelier-routage-grp2.py`](../td2/C-routing/atelier-routage-grp2.py)) | fait |

**Panel et seuil déclarés** : `groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`,
`groq:qwen/qwen3.8-27b` (trois familles), k = 2 sur n = 3. Un membre indisponible reste dans n sans voter.

## Résultats (observés)

- **Vote, lot de base** (un run par modèle) : 16 consensus, tous égaux à la référence, 0 faux, 4
  abstentions (C10, C15, C17, C19). **Run FULL-1** (les cinq modèles dans une même session) : 15 consensus,
  0 faux, 5 abstentions (C09, C10, C15, C17, C19). Le vote s'est abstenu au lieu d'inventer une valeur à
  chaque fois que le panel était en désaccord. La référence n'a été lue qu'après la décision.
- **Faux consensus** : aucun pour le panel fixe *ni dans le lot de base ni dans FULL-1*. La revue croisée a
  montré que cela dépend du run : sur C09, le panel fixe renvoie 0 dans 12 des 40 combinaisons d'un run par
  membre (cas WC-4, [`shared-errors.md`](../td2/B-consensus/results/shared-errors.md)) ; qwen3.8-27b se
  trompe sur C09 dans 3 de ses 5 runs. Des paires de modèles du TD 1 s'accordent bien sur des valeurs
  fausses : C02 dans FULL-1 (gpt-oss-20b et north-mini-code, tous deux 0), C11 (north-mini-code et dots,
  tous deux 0) et C10 (qwen et dots, tous deux 119410, sur deux runs). Un panel qui change un seul membre en
  fait des faux consensus. Les causes sont visibles dans le SQL : un filtre vide lu comme 0 par `COALESCE`,
  et un âge calculé comme une différence d'années malgré la convention imposée par le prompt. DEMO-VOTE
  (synthétique) est traité à part.
- **Règle de routage** : le modèle correct le moins cher est une route OpenRouter gratuite pour la période et
  le produit (les cinq modèles à 6/6 et 4/4), `gpt-oss-20b` pour les familles d'âge et les combinaisons. Le
  quorum est utilisé là où plusieurs familles ont juste. Une **référence indépendante** est utilisée là où
  seule la famille gpt-oss a juste (C10, C15 C17 C19), car un quorum de familles distinctes ne peut pas y
  confirmer la réponse.
- **Simulateur** : la règle du kit et la nôtre prennent la même action sur les sept scénarios (exécuter,
  exécuter, différer, exécuter, s'abstenir, exécuter + revue, s'abstenir). Elles diffèrent par la ressource
  (nos modèles, avec une éligibilité par famille), la vérification (par usage et par famille), la raison
  (elle cite les cellules du TD 1 et nomme les ressources écartées) et le coût payé (0,000134 USD par
  requête sur l'enveloppe de tokens mesurée, contre 0,30 fictif). Un scénario a été ajouté : fournisseur
  préféré indisponible (R2 du modèle de règle).

## Apport à la plénière : là où aucun modèle gratuit ne suffit seul

- Questions où une seule famille a juste dans le lot de base, donc où le quorum s'abstient : **C10, C15,
  C17, C19**.
- Questions où les deux routes OpenRouter à 0 USD (north-mini-code et dots) se trompent : **C08, C10, C11,
  C15, C17, C18**. Ces questions demandent gpt-oss sur le plan gratuit de Groq, dont le quota a été épuisé
  pendant le TD 1 (HTTP 429 sur 6 cellules de base), ou une route payante.
- Cela fixe le prix de la vérification pour le TD 3 : une référence indépendante sur l'âge à la commande et
  sur les combinaisons.

## Causes et hypothèses (non établies)

- *Hypothèse* : 0 attire les erreurs partagées parce que le prompt rend `COALESCE(SUM, 0)` obligatoire. Tout
  filtre faux qui vide l'ensemble donne 0. Trois des quatre valeurs fausses partagées sont 0 (C02, C09, C11),
  ce qui n'est pas un taux mesuré.
- *Hypothèse* : l'erreur d'âge par différence d'années est une habitude d'entraînement partagée. Elle apparaît
  chez des modèles de deux éditeurs alors que le prompt l'interdit.
- *Observé* : le même modèle avec le même prompt à température 0 change de verdict d'un run à l'autre
  (gpt-oss-20b sur C02 et C11, qwen3.8-27b sur C09 et C16, voir [`td1/notes/pivot-td1.md`](../td1/notes/pivot-td1.md)).
  L'éligibilité tirée d'un seul run de base est donc fragile. La règle cite les répétitions quand elles sont
  en désaccord.

## Limites

Vingt questions et quelques runs par modèle : une observation propre à ce lot, pas un taux d'erreur, un
classement permanent ni une garantie du quorum. Les tables de vote utilisent un seul fichier d'expérience à
la fois. Le fichier fusionné `td1/traces-td1.csv` mélange les runs, et `atelier-vote.py` prend la dernière
ligne de chaque membre. WC-3 combine deux runs et sert d'illustration. Les disponibilités du simulateur sont
des hypothèses. Le quorum « 3 sur 5 » de l'énoncé ne peut pas être construit avec des familles distinctes à
partir de nos cinq modèles : gpt-oss-20b et gpt-oss-120b forment une seule famille, ce qui en laisse quatre.
La règle utilise donc 2 sur 3 plus une référence.

## Revues croisées

Chaque groupe a vérifié une étape et en répond, puis a relu les deux autres étapes : six revues en français,
deux par étape, sans constats qui se recoupent, chaque correction dans son propre commit
([`td2/reviews/README.md`](../td2/reviews/README.md)). Effets principaux : le vote refuse les verdicts inconnus
et, sur demande, deux modèles d'une même famille ; le pilote refuse les fichiers qui mélangent les runs ; la
recherche de faux consensus est systématique (C09 trouvé) ; la vérification « non vide » est exécutée ; le
simulateur calcule l'éligibilité, les tokens et la latence à partir des traces ; les retry du TD 1 sont
expliqués (quota de 1000 tokens de sortie par minute de qwen avec une pause de 3 s,
[`retries.md`](../td2/A-quorum/results/retries.md)).

## Contributions

| Groupe | Membres | Étape dont il répond | Revues rédigées |
|---|---|---|---|
| A [1] | Jason ZOH, Yohan ALLOUCHE | étape 1, quorum (`td2/A-quorum/`, `vote_k_sur_n`) | [étape 2](../td2/reviews/revue-A-etape2.md), [étape 3](../td2/reviews/revue-A-etape3.md) |
| B [2] | Roy WEHBE, Enzo SIERRA-GUISSET, Florent SEYDOUX | étape 2, faux consensus (`td2/B-consensus/`) | [étape 1](../td2/reviews/revue-B-etape1.md), [étape 3](../td2/reviews/revue-B-etape3.md) |
| C [3] | Kuresa RAMEN, Paul CHARMOILLE, Thomas ANQUETIN | étape 3, routage (`td2/C-routing/`) | [étape 1](../td2/reviews/revue-C-etape1.md), [étape 2](../td2/reviews/revue-C-etape2.md) |

Le code et les rédactions ont été produits avec l'aide d'une IA, déclarée avec son prompt dans
[`td2/ai-assistance-en.md`](../td2/ai-assistance-en.md) ; les groupes les ont vérifiés et ont rédigé les
revues. La part individuelle de chaque membre reste à compléter par le groupe.

## Prochaines étapes (TD 3)

- Chiffrer le coût des configurations de la règle (modèle seul, 2 sur 3, référence) avec `methode-cout-en.md`,
  à partir des tokens des traces.
- Chiffrer la référence indépendante sur C10 et C15 à C19, et tester si un modèle payant capable de
  raisonnement en supprime le besoin.
- Ajouter `reports/td1.md`. Il n'est pas encore dans le dépôt, alors que le guide de rendu l'exige.

## Commandes (sans réseau, depuis la racine du dépôt)

```bash
python td2/A-quorum/test_vote.py                                   # 19 tests du contrat
python atelier-vote.py                                             # les quatre exemples synthétiques du kit
python td2/A-quorum/run_vote.py --traces td1/traces-td1-base.csv --label base
python td2/A-quorum/run_vote.py --traces td1/traces-raw/traces-td1_full.csv --label full1
python td2/A-quorum/retry_analysis.py                              # retry du TD 1
python td2/B-consensus/explain_wrong_consensus.py
python td2/B-consensus/scan_shared_errors.py                       # chaque valeur fausse partagée, 40 combinaisons de runs
python td2/C-routing/family_evidence.py > td2/C-routing/results/family-evidence.md
python atelier-routage.py                                          # règle du kit (avant)
python td2/C-routing/atelier-routage-grp2.py                       # notre règle (après)
python td2/C-routing/atelier-routage-grp2.py --criterion every-run # éligibilité plus stricte
python td2/check_prompts.py
```
