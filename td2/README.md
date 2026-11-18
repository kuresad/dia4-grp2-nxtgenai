# TD 2: the quorum, then the routing rule (18 November 2026)

No model call in TD 2: every script replays the stored TD 1 traces of [`../td1/`](../td1/) offline. The
`vote_k_sur_n` method is in the kit's [`skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py) at the
root. Report: [`../reports/td2.md`](../reports/td2.md).

| Folder | Step | Main files |
|---|---|---|
| [`A-quorum/`](A-quorum/) | 1. k-of-n vote | [`test_vote.py`](A-quorum/test_vote.py) → [`voting-tests-en.csv`](A-quorum/voting-tests-en.csv); driver [`run_vote.py`](A-quorum/run_vote.py) → twenty decisions [`results/vote-base.md`](A-quorum/results/vote-base.md), [`results/vote-full1.md`](A-quorum/results/vote-full1.md) |
| [`B-consensus/`](B-consensus/) | 2. wrong consensus | [`wrong-consensus.md`](B-consensus/wrong-consensus.md); evidence script [`explain_wrong_consensus.py`](B-consensus/explain_wrong_consensus.py) → [`results/explain-wrong-consensus.txt`](B-consensus/results/explain-wrong-consensus.txt) |
| [`C-routing/`](C-routing/) | 3. routing rule | [`routing-rule.md`](C-routing/routing-rule.md); [`family_evidence.py`](C-routing/family_evidence.py) → [`results/family-evidence.md`](C-routing/results/family-evidence.md); simulator [`atelier-routage-grp2.py`](C-routing/atelier-routage-grp2.py); outputs [`simulator-before.jsonl`](C-routing/results/simulator-before.jsonl) / [`simulator-after.jsonl`](C-routing/results/simulator-after.jsonl) |
| this folder | prompts, AI help | [`check_prompts.py`](check_prompts.py) → [`check-prompts.txt`](check-prompts.txt); [`ai-assistance-en.md`](ai-assistance-en.md) |

Declared panel: `groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`,
`groq:qwen/qwen3.8-27b`, k = 2 of n = 3.

## Commands (from the repository root, no network)

```bash
python td2/A-quorum/test_vote.py
python atelier-vote.py
python td2/A-quorum/run_vote.py --traces td1/traces-td1-base.csv --label base
python td2/A-quorum/run_vote.py --traces td1/traces-raw/traces-td1_full.csv --label full1
python td2/B-consensus/explain_wrong_consensus.py > td2/B-consensus/results/explain-wrong-consensus.txt
python td2/C-routing/family_evidence.py > td2/C-routing/results/family-evidence.md
python atelier-routage.py > td2/C-routing/results/simulator-before.jsonl
python td2/C-routing/atelier-routage-grp2.py > td2/C-routing/results/simulator-after.jsonl
python td2/check_prompts.py > td2/check-prompts.txt
```

On Windows, set `PYTHONIOENCODING=utf-8` before redirecting the output of the scripts that print accents
or arrows (`explain_wrong_consensus.py`, `family_evidence.py`).
