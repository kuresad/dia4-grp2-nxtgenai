# TD 2 report: the quorum, then the routing rule

Sub-group DIA4 GRP2, session of 18 November 2026, pack `2026-10-14-students-1`. **No model was called in
TD 2**: every figure below replays the stored TD 1 traces offline (`nature = real`), except the
simulations and the synthetic DEMO-VOTE, which are labelled as such. The prompts did not change
([`prompts-en.md`](../td1/prompts-en.md); 319/319 trace fingerprints match, [`td2/check-prompts.txt`](../td2/check-prompts.txt)).

## What was attempted and completed

| Step | Deliverable | File | Status |
|---|---|---|---|
| 1 | `vote_k_sur_n` completed | [`skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py) (`Orchestrateur.vote_k_sur_n`) | done |
| 1 | Contract tests: agreement, disagreement, unavailable members, duplicate route, invalid k, 3-of-5, wrong consensus | [`td2/A-quorum/test_vote.py`](../td2/A-quorum/test_vote.py) → [`voting-tests-en.csv`](../td2/A-quorum/voting-tests-en.csv), [`test-vote.txt`](../td2/A-quorum/results/test-vote.txt) | 19/19 pass (16 before the cross-reviews) |
| 1 | Driver: `atelier-vote.py --traces … --case Cxx` on the twenty questions | [`td2/A-quorum/run_vote.py`](../td2/A-quorum/run_vote.py) | done |
| 1 | **Table of the twenty decisions** (panel and k declared below) | [`vote-base.md`](../td2/A-quorum/results/vote-base.md) (base batch), [`vote-full1.md`](../td2/A-quorum/results/vote-full1.md) (run FULL-1); CSV and raw JSONL next to them | done |
| 2 | Commented wrong consensus | [`td2/B-consensus/wrong-consensus.md`](../td2/B-consensus/wrong-consensus.md), evidence [`explain-wrong-consensus.txt`](../td2/B-consensus/results/explain-wrong-consensus.txt) | done |
| 3 | One-page routing rule with the TD 1 cells | [`td2/C-routing/routing-rule.md`](../td2/C-routing/routing-rule.md), evidence [`family-evidence.md`](../td2/C-routing/results/family-evidence.md) | done |
| 3 | Simulator outputs before and after adaptation | [`simulator-before.jsonl`](../td2/C-routing/results/simulator-before.jsonl) (kit `atelier-routage.py`), [`simulator-after.jsonl`](../td2/C-routing/results/simulator-after.jsonl) ([`atelier-routage-grp2.py`](../td2/C-routing/atelier-routage-grp2.py)) | done |

**Declared panel and threshold**: `groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`,
`groq:qwen/qwen3.8-27b` (three families), k = 2 of n = 3. An unavailable member stays in n without a vote.

## Results (observed)

- **Vote, base batch** (one run per model): 16 consensus, all equal to the reference, 0 wrong, 4
  abstentions (C10, C15, C17, C19). **Run FULL-1** (the five models in one session): 15 consensus, 0 wrong,
  5 abstentions (C09, C10, C15, C17, C19). The vote abstained instead of inventing a value every time the
  panel disagreed. The reference was only read after the decision.
- **Wrong consensus**: none from the fixed panel *in the base batch or in FULL-1*. The cross-review found
  that this depends on the run: on C09 the fixed panel returns 0 in 12 of the 40 combinations of one run per
  member (case WC-4, [`shared-errors.md`](../td2/B-consensus/results/shared-errors.md)); qwen3.8-27b is
  wrong on C09 in 3 of its 5 runs. Pairs of TD 1 models do agree on wrong values:
  C02 in FULL-1 (gpt-oss-20b and north-mini-code, both 0), C11 (north-mini-code and dots, both 0) and
  C10 (qwen and dots, both 119410, from two runs). A panel that swaps one member turns them into wrong
  consensus. The causes are visible in the SQL: an empty filter read as 0 by `COALESCE`, and age computed
  as a difference of years despite the binding convention of the prompt. DEMO-VOTE (synthetic) is treated
  apart.
- **Routing rule**: the cheapest correct model is a free OpenRouter route for period and product (all five
  models 6/6 and 4/4), `gpt-oss-20b` for the age families and combinations. The quorum is used where
  several families are right. An **independent reference** is used where only the gpt-oss family is right
  (C10, C15 C17 C19), because a quorum of distinct families cannot confirm the answer there.
- **Simulator**: the kit rule and ours take the same action on the seven scenarios (run, run, defer,
  run, abstain, run + review, abstain). They differ in the resource (our models, with eligibility by
  family), the checking (by use and family), the reason (it cites the TD 1 cells and names the resources
  ruled out) and the paid cost (0.000134 USD per request on the measured token envelope, against the
  fictitious 0.30). One scenario was added: preferred provider unavailable (R2 of the template).

## Plenary input: where no free model is enough on its own

- Questions where only one family is right in the base batch, so the quorum abstains: **C10, C15, C17,
  C19**.
- Questions where both 0-USD OpenRouter routes (north-mini-code and dots) are wrong: **C08, C10, C11, C15,
  C17, C18**. These questions need gpt-oss on the Groq free plan, whose quota ran out during TD 1 (HTTP
  429 on 6 base cells), or a paid route.
- This sets the price of checking for TD 3: an independent reference on age at the order and on
  combinations.

## Causes and hypotheses (not established)

- *Hypothesis*: 0 attracts shared errors because the prompt makes `COALESCE(SUM, 0)` mandatory. Any wrong
  filter that empties the set gives 0. Three of the four shared wrong values are 0 (C02, C09, C11), which
  is not a measured rate.
- *Hypothesis*: the year-difference age error is a shared training habit. It appears in two vendors'
  models although the prompt forbids it.
- *Observed*: the same model and prompt at temperature 0 change verdict between runs (gpt-oss-20b on C02
  and C11, qwen3.8-27b on C09 and C16, see [`td1/notes/pivot-td1.md`](../td1/notes/pivot-td1.md)). Eligibility from one base run is
  therefore fragile. The rule cites the repetitions when they disagree.

## Limits

Twenty questions and a few runs per model: a batch-specific observation, not an error rate, a permanent
ranking or a guarantee of the quorum. The vote tables use one experiment file at a time. The merged
`td1/traces-td1.csv` mixes runs, and `atelier-vote.py` takes the last row per member. WC-3 combines two runs
and is an illustration. Simulator availabilities are assumptions. The "3-of-5" quorum of the statement
cannot be built with distinct families from our five models: gpt-oss-20b and gpt-oss-120b are one family,
which leaves four. The rule therefore uses 2-of-3 plus a reference.

## Cross-reviews

Each group checked and answers for one step, then reviewed the two other steps: six reviews in French, two
per step, without overlapping findings, each fix in its own commit
([`td2/reviews/README.md`](../td2/reviews/README.md)). Main effects: the vote refuses unknown verdicts and,
on request, two models of one family; the driver refuses files that mix runs; the wrong consensus search is
systematic (C09 found); the non-empty check is executed; the simulator computes eligibility, tokens and
latency from the traces; the TD 1 retries are explained (qwen's 1000 output tokens per minute quota at a 3 s
pause, [`retries.md`](../td2/A-quorum/results/retries.md)).

## Contributions

| Group | Members | Step answered for | Reviews written |
|---|---|---|---|
| A [1] | Jason ZOH, Yohan ALLOUCHE | step 1, quorum (`td2/A-quorum/`, `vote_k_sur_n`) | [step 2](../td2/reviews/revue-A-etape2.md), [step 3](../td2/reviews/revue-A-etape3.md) |
| B [2] | Roy WEHBE, Enzo SIERRA-GUISSET, Florent SEYDOUX | step 2, wrong consensus (`td2/B-consensus/`) | [step 1](../td2/reviews/revue-B-etape1.md), [step 3](../td2/reviews/revue-B-etape3.md) |
| C [3] | Kuresa RAMEN, Paul CHARMOILLE, Thomas ANQUETIN | step 3, routing (`td2/C-routing/`) | [step 1](../td2/reviews/revue-C-etape1.md), [step 2](../td2/reviews/revue-C-etape2.md) |

The code and the write-ups were produced with AI assistance, declared with its prompt in
[`td2/ai-assistance-en.md`](../td2/ai-assistance-en.md); the groups checked them and wrote the reviews. Each
member's individual part is to be completed by the group.

## Next steps (TD 3)

- Cost the configurations of the rule (single model, 2-of-3, reference) with `methode-cout-en.md`, from
  the tokens of the traces.
- Price the independent reference on C10 and C15 to C19, and test whether a reasoning-capable paid model
  removes the need for it.
- Add `reports/td1.md`. It is not in the repository yet, though the submission guide requires it.

## Commands (no network, from the repository root)

```bash
python td2/A-quorum/test_vote.py                                   # 19 contract tests
python atelier-vote.py                                             # the kit's four synthetic examples
python td2/A-quorum/run_vote.py --traces td1/traces-td1-base.csv --label base
python td2/A-quorum/run_vote.py --traces td1/traces-raw/traces-td1_full.csv --label full1
python td2/A-quorum/retry_analysis.py                              # TD 1 retries
python td2/B-consensus/explain_wrong_consensus.py
python td2/B-consensus/scan_shared_errors.py                       # every shared wrong value, 40 run combinations
python td2/C-routing/family_evidence.py > td2/C-routing/results/family-evidence.md
python atelier-routage.py                                          # kit rule (before)
python td2/C-routing/atelier-routage-grp2.py                       # our rule (after)
python td2/C-routing/atelier-routage-grp2.py --criterion every-run # stricter eligibility
python td2/check_prompts.py
```
