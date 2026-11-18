# Trustworthy generative AI - sub-group DIA4 GRP2
ESILV, Next-Generation AI (MESIIN475926), Didier Parisot. Public repository of the sub-group for TD 1, 2 and 3.

| Item | Value |
|---|---|
| Sub-group | GRP2 |
| Members | Jason ZOH, Kuresa RAMEN, Paul CHARMOILLE, Enzo SIERRA-GUISSET, Roy WEHBE, Yohan ALLOUCHE, Florent SEYDOUX, Thomas ANQUETIN |
| Pack version | `2026-10-14-students-1` (kit of 14 October 2026) |
| Database | `data/boutique.sqlite`, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`, seed 20260925, identical to `data/manifest.json` |
| Environment | Windows 11, Python 3.14.7, SQLite 3.50.4, `requests` in a `.venv` (only for `check_access.py`); the skeleton and scripts use the standard library |
| Repository URL | <https://github.com/kuresad/dia4-grp2-nxtgenai> |

## Layout

```text
.
├── README.md                  this file
├── reports/                   one session report per TD (td1.md, td2.md, td3.md)
├── td1/                       TD 1 deliverables: references, traces, comparison, summary, prompts
├── td2/                       TD 2 deliverables: vote (A-quorum), wrong consensus (B-consensus), routing (C-routing)
├── td3/                       TD 3 (to come)
│
│   Kit, shared by the three TDs (kept at the root: each script looks for its resources next to itself)
├── skeleton-multi-llm-en.py   multi-model orchestrator; vote_k_sur_n completed in TD 2
├── atelier-vote.py            TD 2 vote workshop (kit, unchanged)
├── atelier-routage.py         TD 2/3 routing simulator (kit, unchanged)
├── sandbox_sqlite.py          read-only SQL sandbox
├── check_access.py            access check of the five models
├── verify-data.py             hashes of the database and CSV files
├── data/                      boutique.sqlite and its CSV files, manifest
├── schema.sql, questions-td1.json, modeles-autorises.json
└── .gitignore, .gitattributes keys, environments and caches stay out; kit data byte-identical
```

## Status per session

| TD | Date | Folder | Report | Summary |
|---|---|---|---|---|
| TD 1 | 21 October 2026 | [`td1/`](td1/README.md) | `reports/td1.md` (**missing**) | 20 references; 319 attempts over 11 runs of 5 models; base batch: gpt-oss-20b 20/20, gpt-oss-120b 18/20, qwen3.8-27b 16/20, dots-3-note 14/20, north-mini-code 10/20 |
| TD 2 | 18 November 2026 | [`td2/`](td2/README.md) | [`reports/td2.md`](reports/td2.md) | `vote_k_sur_n` (16/16 tests); fixed 2-of-3 panel on the base batch: 16 consensus, 0 wrong, 4 abstentions; wrong consensus explained (C02, C10, C11, DEMO-VOTE); routing rule and simulator before/after |
| TD 3 | to come | `td3/` | `reports/td3.md` | cost worksheet, use case, slides, demonstration |

## Quick check (no network, from the root)

```bash
python verify-data.py                                   # "ok": true
python check_access.py --no-network                     # Python, base and CSV fingerprints
python skeleton-multi-llm-en.py --rates --state td1/traces-td1-base.jsonl --reference td1/reference-td1.csv
python td2/A-quorum/test_vote.py                        # 16/16 tests pass
python td2/C-routing/atelier-routage-grp2.py            # our routing rule on the scenarios
```

Every TD 1 and TD 2 command is listed in [`td1/README.md`](td1/README.md) and [`td2/README.md`](td2/README.md).
A new model run needs `GROQ_API_KEY` / `OPENROUTER_API_KEY` in the shell, never in a file of the repository.

## Repository hygiene

No key, no `.env`, no account screenshot is committed. The kit's `.gitignore` is at the root
(environment files, keys, `.venv/`, caches, `ready-for-td1.txt`). The saved `check_access.py` output of
18 October 2026 (all five models OK) stays on the members' machines, as the `.gitignore` provides.

## AI assistance

AI-assisted work is declared with the prompts as used: [`td2/ai-assistance-en.md`](td2/ai-assistance-en.md).

## Open blocks

- `reports/td1.md` is still to be written.
- TD 2 contributions of each member, in [`reports/td2.md`](reports/td2.md).
- TD 1: member roles B, F, G, H, the operator of `FULL-1` and of `A-op2-1` ([`td1/README.md`](td1/README.md)).
