# TD 1: five models, twenty questions (21 October 2026)

Deliverables of TD 1. Paths stored inside the files (`source_file` of the traces, `trace_file` of the
comparison CSV, such as `traces-raw/state-A.jsonl`) are relative to this `td1/` folder. The kit code and
the database used to produce them are at the [repository root](../README.md).

## Deliverables

| Deliverable | File | Status |
|---|---|---|
| Twenty references, query and value | [`reference-td1.csv`](reference-td1.csv) | Done in step 1; re-checked by SQL and by an independent Python recomputation, all 20 equal ([note](notes/reference-checks-td1.md)) |
| Every attempt, all runs | [`traces-td1.csv`](traces-td1.csv), [`traces-td1.jsonl`](traces-td1.jsonl) | 319 attempts, 11 runs, all `nature = real`; the JSONL holds the same rows as the CSV, in the skeleton's state format |
| Base batch only (100 cells) | [`traces-td1-base.csv`](traces-td1-base.csv), [`traces-td1-base.jsonl`](traces-td1-base.jsonl) | 106 attempts: 100 first attempts + 6 retries after HTTP 429 (the rows of `traces-td1.csv` with `in_base_batch = yes`) |
| Raw files of each operator | [`traces-raw/`](traces-raw/) | Kept unchanged |
| One final row per model x question | [`model-question-comparison-en_J.csv`](model-question-comparison-en_J.csv) | 100 rows from the base batch, cause of every failure in `explanation`; [`model-question-comparison-en_R.csv`](model-question-comparison-en_R.csv) is the earlier version built from `FULL-1` only |
| Pivot view models x questions | [`notes/pivot-td1.md`](notes/pivot-td1.md) | Generated from the comparison CSV; also every run and the cells that change between runs |
| Five-model summary | [`five-model-summary-en.csv`](five-model-summary-en.csv) | Index, dated prices or N/A with reason, access, results by family |
| Prompts as used | [`prompts-en.md`](prompts-en.md) | One version, unchanged in TD 2 (fingerprints checked) |
| Session report | `../reports/td1.md` | **Missing**: to be written by the group |

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

## Commands to replay (from the repository root)

```bash
python verify-data.py                          # hashes of the base and CSV files, "ok": true
python check_access.py --no-network            # Python, base and CSV fingerprints, no model call
python skeleton-multi-llm-en.py --rates --state td1/traces-td1-base.jsonl --reference td1/reference-td1.csv
```

These commands make no network call. A new model run (not needed for TD 2 or TD 3) is, for one model:

```bash
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --reference td1/reference-td1.csv --state state-new.jsonl --out traces-new.csv
```

with `GROQ_API_KEY` / `OPENROUTER_API_KEY` set in the shell (never in a file of the repository).

## Open blocks

- Member names, roles B, F, G, H, the operator of `FULL-1` and of `A-op2-1`.
- The group used far more calls than the 100-cell base batch (319 attempts: 239 Groq, 80 OpenRouter):
  the repetitions were not in the planned allocation. They are kept and labelled, never mixed into the
  base-batch rates.
