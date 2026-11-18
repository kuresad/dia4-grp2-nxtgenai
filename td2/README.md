# TD 2 : le quorum, puis la règle de routage (18 novembre 2026)

Aucun appel aux modèles au TD 2 : chaque script rejoue hors ligne les traces stockées du TD 1
([`../td1/`](../td1/)). La méthode `vote_k_sur_n` est dans le
[`skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py) du kit, à la racine. Rapport :
[`../reports/td2.md`](../reports/td2.md). Revues croisées : [`reviews/`](reviews/README.md).

| Dossier | Étape (auteurs) | Fichiers principaux |
|---|---|---|
| [`A-quorum/`](A-quorum/) | 1. vote k-sur-n (groupe A) | tests [`test_vote.py`](A-quorum/test_vote.py) → [`voting-tests-en.csv`](A-quorum/voting-tests-en.csv) ; pilote [`run_vote.py`](A-quorum/run_vote.py) → les vingt décisions [`results/vote-base.md`](A-quorum/results/vote-base.md), [`results/vote-full1.md`](A-quorum/results/vote-full1.md) ; retry du TD 1 [`retry_analysis.py`](A-quorum/retry_analysis.py) → [`results/retries.md`](A-quorum/results/retries.md) |
| [`B-consensus/`](B-consensus/) | 2. faux consensus (groupe B) | commentaire [`wrong-consensus.md`](B-consensus/wrong-consensus.md) ; [`explain_wrong_consensus.py`](B-consensus/explain_wrong_consensus.py) → [`results/explain-wrong-consensus.txt`](B-consensus/results/explain-wrong-consensus.txt) ; recherche systématique [`scan_shared_errors.py`](B-consensus/scan_shared_errors.py) → [`results/shared-errors.md`](B-consensus/results/shared-errors.md) ; sondes [`probes.py`](B-consensus/probes.py) |
| [`C-routing/`](C-routing/) | 3. règle de routage (groupe C) | règle d'une page [`routing-rule.md`](C-routing/routing-rule.md) ; [`family_evidence.py`](C-routing/family_evidence.py) → [`results/family-evidence.md`](C-routing/results/family-evidence.md) ; simulateur [`atelier-routage-grp2.py`](C-routing/atelier-routage-grp2.py) ; sorties [avant](C-routing/results/simulator-before.jsonl) / [après](C-routing/results/simulator-after.jsonl) / [après, critère « tous les runs »](C-routing/results/simulator-after-every-run.jsonl) |
| [`reviews/`](reviews/README.md) | revues croisées | six revues (deux par étape) avec le commit de chaque correction ; copies dans `<étape>/reviews/` |
| ce dossier | commun | [`common.py`](common.py) (chemins, vote, conversion des traces, familles) ; [`check_prompts.py`](check_prompts.py) → [`check-prompts.txt`](check-prompts.txt) ; [`ai-assistance-en.md`](ai-assistance-en.md) |

Panel déclaré : `groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`,
`groq:qwen/qwen3.8-27b`, k = 2 sur n = 3.

## Commandes (depuis la racine du dépôt, sans réseau)

```bash
python td2/A-quorum/test_vote.py > td2/A-quorum/results/test-vote.txt
python atelier-vote.py
python td2/A-quorum/run_vote.py --traces td1/traces-td1-base.csv --label base > td2/A-quorum/results/vote-base.md
python td2/A-quorum/run_vote.py --traces td1/traces-raw/traces-td1_full.csv --label full1 > td2/A-quorum/results/vote-full1.md
python td2/A-quorum/retry_analysis.py > td2/A-quorum/results/retries.md
python td2/B-consensus/explain_wrong_consensus.py > td2/B-consensus/results/explain-wrong-consensus.txt
python td2/B-consensus/scan_shared_errors.py > td2/B-consensus/results/shared-errors.md
python td2/C-routing/family_evidence.py > td2/C-routing/results/family-evidence.md
python atelier-routage.py > td2/C-routing/results/simulator-before.jsonl
python td2/C-routing/atelier-routage-grp2.py > td2/C-routing/results/simulator-after.jsonl
python td2/C-routing/atelier-routage-grp2.py --criterion every-run > td2/C-routing/results/simulator-after-every-run.jsonl
python td2/check_prompts.py > td2/check-prompts.txt
python td2/reviews/sync_copies.py                  # recopie les revues dans chaque dossier d'étape
```

`run_vote.py` refuse un fichier qui mélange plusieurs runs (par exemple `td1/traces-td1.csv`) : un fichier
par expérience.
