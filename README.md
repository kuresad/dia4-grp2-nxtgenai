# Trustworthy generative AI - sub-group DIA4 GRP2
ESILV, Next-Generation AI (MESIIN475926), Didier Parisot. Public repository of the sub-group for TD 1, 2 and 3.

| Item | Value |
|---|---|
| Sub-group | GRP2  |
| Members | Jason ZOH, Kuresa RAMEN, Paul CHARMOILLE, Enzo SIERRA-GUISSET, Roy WEHBE, Yohan ALLOUCHE, Florent SEYDOUX, Thomas ANQUETIN |
| Pack version | `2026-10-14-students-1` (kit of 14 October 2026) |
| Database | `data/boutique.sqlite`, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`, seed 20260925, identical to `data/manifest.json` |
| Environment | Windows 11, Python 3.14.7, SQLite 3.50.4, `requests` in a `.venv` (only for `check_access.py`); the skeleton and scripts use the standard library |
| Repository URL | [[lien repository]](https://github.com/kuresad/dia4-grp2-nxtgenai) |

## Status after TD 1 (21 October 2026)

| Deliverable | File | Status |
|---|---|---|
| Twenty references, query and value | [`reference-td1.csv`](reference-td1.csv) | Done in step 1; re-checked by SQL and by an independent Python recomputation, all 20 equal ([note](notes/reference-checks-td1.md)) |
| Every attempt, all runs | [`traces-td1.csv`](traces-td1.csv), [`traces-td1.jsonl`](traces-td1.jsonl) | 319 attempts, 11 runs, all `nature = real`; the JSONL holds the same rows as the CSV, in the skeleton's state format |
| Base batch only (100 cells) | [`traces-td1-base.csv`](traces-td1-base.csv), [`traces-td1-base.jsonl`](traces-td1-base.jsonl) | 106 attempts: 100 first attempts + 6 retries after HTTP 429 (the rows of `traces-td1.csv` with `in_base_batch = yes`) |
| Raw files of each operator | [`traces-raw/`](traces-raw/) | Kept unchanged |
| One final row per model x question | [`model-question-comparison-en_J.csv`](model-question-comparison-en_J.csv) | 100 rows from the base batch, cause of every failure in `explanation`; [`model-question-comparison-en_R.csv`](model-question-comparison-en_R.csv) is the earlier version built from `FULL-1` only |
| Pivot view models x questions | [`notes/pivot-td1.md`](notes/pivot-td1.md) | Generated from the comparison CSV; also every run and the cells that change between runs |
| Five-model summary | [`five-model-summary-en.csv`](five-model-summary-en.csv) | Index, dated prices or N/A with reason, access, results by family |

## Status after TD 2 (18 November 2026)

Report: [`reports/td2.md`](reports/td2.md). No model call in TD 2: the stored TD 1 traces are replayed offline.

| Deliverable | File | Status |
|---|---|---|
| `vote_k_sur_n` completed | [`skeleton-multi-llm-en.py`](skeleton-multi-llm-en.py) | Done; 16/16 contract tests ([`td2/A-quorum/voting-tests-en.csv`](td2/A-quorum/voting-tests-en.csv)) |
| Declared panel and threshold | gpt-oss-120b (Groq), north-mini-code:free (OpenRouter), qwen3.8-27b (Groq), 2-of-3 | Fixed panel of the statement |
| Twenty decisions of the vote | [`td2/A-quorum/results/vote-base.md`](td2/A-quorum/results/vote-base.md), [`vote-full1.md`](td2/A-quorum/results/vote-full1.md) | Base: 16 consensus (0 wrong), 4 abstentions |
| Commented wrong consensus | [`td2/B-consensus/wrong-consensus.md`](td2/B-consensus/wrong-consensus.md) | C02 (FULL-1), C10, C11 real; DEMO-VOTE synthetic, kept apart |
| One-page routing rule | [`td2/C-routing/routing-rule.md`](td2/C-routing/routing-rule.md) | Cites the TD 1 cells ([`family-evidence.md`](td2/C-routing/results/family-evidence.md)) |
| Simulator before / after | [`simulator-before.jsonl`](td2/C-routing/results/simulator-before.jsonl), [`simulator-after.jsonl`](td2/C-routing/results/simulator-after.jsonl) | Kit `atelier-routage.py`, then [`td2/C-routing/atelier-routage-grp2.py`](td2/C-routing/atelier-routage-grp2.py) |
| Prompts | [`prompts-en.md`](prompts-en.md) | Unchanged since TD 1 (319/319 fingerprints match) |
| AI assistance | [`td2/ai-assistance-en.md`](td2/ai-assistance-en.md) | Prompt kept as used |

Replay (no network): see the command block at the end of [`reports/td2.md`](reports/td2.md).

## The runs

All runs used the same prompt (same fingerprint per question), the same references and the kit
parameters. The base batch follows the A-E allocation of the protocol, one run per model; the other
runs are repetitions, each started with its own `--state`/`--out` files, so they are separate
experiments and never count as retries.

| run_id | Operator | Model | Raw file | Start (UTC) | Base batch |
|---|---|---|---|---|---|
| `FULL-1` | Enzo | all five models in one `--run` | `traces-raw/traces-td1_full.csv` | 2026-10-21 13:50 | yes for E (Dots) only |
| `A-jason-1` | Jason (A) | `groq:openai/gpt-oss-120b` | `traces-raw/state-A.jsonl` | 14:12 | yes |
| `B-1` | Yohan (B) | `groq:openai/gpt-oss-20b` | `traces-raw/traces-B.csv` | 14:14 | yes |
| `D-kuresa-1` | Kuresa (D) | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D-Kuresa.jsonl` | 14:17 | yes |
| `D-paul-1` | Paul | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D-Paul.jsonl` | 14:17 | repetition |
| `A-op2-1` | kuresa | `groq:openai/gpt-oss-120b` | `traces-raw/trace_A.csv` | 14:20 | repetition |
| `A-jason-2` | Jason | `groq:openai/gpt-oss-120b` | `traces-raw/state-A_2.jsonl` | 14:31 | repetition |
| `D-paul-2` | Paul | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D_2-Paul.jsonl` | 14:32 | repetition |
| `D-kuresa-2` | Kuresa | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D-Kuresa2.jsonl` | 14:35 | repetition |
| `C-jason-1` | Florent | `openrouter:cohere/north-mini-code:free` | `traces-raw/state-C.jsonl` | 14:37 | yes |
| `E-jason-1` | Jason  | `openrouter:dots-studio/dots-3-note-preview:free` | `traces-raw/state-E-Jason.jsonl` | 19:18 | repetition |

## Commands to replay

From the repository root, after `python -m venv .venv` and `.venv\Scripts\python.exe -m pip install requests`
(only `check_access.py` needs it). Use `python3` on Linux and macOS.

```bash
python verify-data.py                          # hashes of the base and CSV files, "ok": true
python check_access.py --no-network            # Python, base and CSV fingerprints, no model call
python skeleton-multi-llm-en.py --rates --state traces-td1-base.jsonl   # rates of the base batch
```

These commands make no network call. A new model run (not needed for TD 2 or TD 3) is, for one model:

```bash
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --state state-new.jsonl --out traces-new.csv
```

with `GROQ_API_KEY` / `OPENROUTER_API_KEY` set in the shell (never in a file of the repository).

## Repository hygiene

No key, no `.env`, no account screenshot is committed. The kit's `.gitignore` is at the root
(environment files, keys, `.venv/`, caches, `ready-for-td1.txt`). The saved `check_access.py` output of
18 October 2026 (all five models OK) stays on the members' machines, as the `.gitignore` provides.

## Open blocks

- Member names, roles B, F, G, H, the operator of `FULL-1` and of `A-op2-1`.
- The group used far more calls than the 100-cell base batch (319 attempts: 239 Groq, 80 OpenRouter):
  the repetitions were not in the planned allocation. They are kept and labelled, never mixed into the
  base-batch rates.
- `reports/td1.md` and member contributions for TD 2 are still to be written by the group (see [`reports/td2.md`](reports/td2.md)).
