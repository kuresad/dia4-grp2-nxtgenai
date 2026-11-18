# TD 2 step 2: the wrong consensus

Evidence: [`results/explain-wrong-consensus.txt`](results/explain-wrong-consensus.txt), produced offline by
[`explain_wrong_consensus.py`](explain_wrong_consensus.py) (`python td2/B-consensus/explain_wrong_consensus.py`):
every SQL is read from the stored traces, re-executed read-only through `sandbox_sqlite.py`, and checked
against a plain-Python recomputation from the CSV files (no SQL). The vote is the group's `vote_k_sur_n`.

**Measured result first.** With the declared panel, the 2-of-3 quorum
{`groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`, `groq:qwen/qwen3.8-27b`} returns
**no wrong consensus** on the twenty questions, in the base batch (16 consensus, all equal to the
reference, 4 abstentions) or in run FULL-1 (15 and 5): [`vote-base.md`](../A-quorum/results/vote-base.md),
[`vote-full1.md`](../A-quorum/results/vote-full1.md). The cases below are pairs of TD 1 models that agree on
the same wrong value. They show what a panel built differently would have returned. The two-model agreement
is not the result of the fixed panel. Dots is not a member of that panel.

## WC-1 (main case): C02, run FULL-1, real batch

- **Question** (C02, age on a reference date): revenue of customers who are exactly 25 years old (completed
  age) on 2026-09-25. **Reference** 590320 (`reference-td1.csv`, re-executed; Python recomputation 590320
  over 82 order lines).
- **Nature**: real batch, stored trace replayed offline. One run, five models, same prompt
  (`traces-raw/traces-td1_full.csv`, 2026-10-21 13:50).
- **Agreeing models**: `groq:openai/gpt-oss-20b` → **0**, `openrouter:cohere/north-mini-code:free` → **0**.
  Two families, the same wrong value.
- **Cause in the SQL**: the two errors are different, and both end up on an empty set:

```sql
-- gpt-oss-20b: the 25 years are never subtracted -> customers born in the last 12 months (age 0)
WHERE c.birth_date > '2025-09-25' AND c.birth_date <= '2026-09-25'            -- 0 matching lines
-- north-mini-code: correct age window, plus an invented filter on the order date
WHERE ... c.birth_date <= date('2026-09-25','-25 years') AND c.birth_date > date('2026-09-25','-26 years')
  AND o.date >= '2026-09-25 00:00:00' AND o.date < '2026-09-26 00:00:00'      -- no order after 2026-09-20
```

  `COALESCE(SUM(...), 0)`, required by the prompt, turns any empty filter into 0. **0 is the attractor
  value of a wrong filter**: independent errors converge on it, so two models agreeing on 0 is weak evidence.
- **Declared quorum, 2-of-3**: fixed panel → `{"consensus": true, "value": 590320, "votes": 2}` (120b and
  qwen), **correct**. Alternative panel {gpt-oss-20b, north-mini-code, qwen3.8-27b} (the cheapest gpt-oss
  model in place of 120b) → `{"consensus": true, "value": 0, "votes": 2}`, a **wrong consensus**.
- **Independent check**: a *non-empty population* probe. Execute the age filter alone and count the order
  lines: 82, all with a price and a quantity > 0, so a revenue of 0 is impossible. It runs on the
  database, needs no model, and refutes the wrong consensus 0. This is the dashboard check of the
  age families in our [routing rule](../C-routing/routing-rule.md).

## WC-3 (same non-zero wrong value from two families): C10, real but across two runs

- **Question** (C10, age at the time of the order): revenue of orders placed by customers aged exactly 25
  on the order date. **Reference** 558980 (Python recomputation over 73 lines).
- **Nature**: real values, but from two different runs: qwen in the base batch (`D-kuresa-1`,
  `traces-raw/state-D-Kuresa.jsonl`), dots in a repetition (`E-jason-1`, `traces-raw/state-E-Jason.jsonl`).
  The panel below is recomposed across runs, as an **illustration only**.
- **Agreeing models**: `groq:qwen/qwen3.8-27b` → **119410**, `openrouter:dots-studio/dots-3-note-preview:free`
  → **119410**.
- **Cause in the SQL**: both compute age as a **difference of calendar years**, and both miss the customers
  whose year difference is 26 but whose birthday has not yet come in the year of the order:

```sql
-- dots: one branch only
WHERE year(o.date) - year(c.birth_date) = 25 AND (month, day of order) >= (month, day of birth)
-- qwen: the same branch, plus a second one written with 24 instead of 26 (age 23), which matches 0 lines
   OR (year(o.date) - year(c.birth_date) = 24 AND (month, day of order) < (month, day of birth))
```

  Re-executed read-only: branch "difference 25, birthday reached" = 119410 over 14 lines; missing branch
  "difference 26, birthday not reached" = 439570 over 59 lines; 119410 + 439570 = 558980, the reference.
  This is the "convention broken" cause of CM2, shared by two vendors, although the binding conventions
  of the prompt say "computed from month and day, never from the year difference alone"
  ([`prompts-en.md`](../../prompts-en.md)): writing the convention in the prompt did not prevent it. gpt-oss-120b avoids it with date
  arithmetic: `date(o.date) >= date(c.birth_date,'+25 years') AND date(o.date) < date(c.birth_date,'+26 years')`.
- **Declared quorum, 2-of-3**: fixed panel (base runs) → `{"consensus": false, "value": null, "votes": 1}`,
  abstention (120b 558980, north 0, qwen 119410). Panel {gpt-oss-120b, qwen3.8-27b, dots-3-note} (across runs) →
  `{"consensus": true, "value": 119410, "votes": 2}`, a **wrong consensus that outvotes the only right model**.
- **Independent check**: a reference computed another way (Python recomputation, or a second query written
  with date arithmetic by a member). A different panel is not a guarantee: on C10 only the gpt-oss family is
  right in every run, so any quorum of distinct families either abstains or agrees on 119410.

## WC-2 (short): C11, base batch

`cohere/north-mini-code:free` (`C-jason-1`) and `dots-3-note` (`FULL-1`) both return 0 against 446690.
Fixed panel: consensus 446690, correct. Panel of the two `:free` OpenRouter models with gpt-oss-120b:
consensus 0. The same non-empty probe (60 matching lines) refutes it.

## DEMO-VOTE: supplied synthetic case, kept apart from our counts

Constructed teaching material from the TD 2 statement, not model output or shop data. One sale on
2026-01-01, 100 cents; period [2026-01-01, 2026-01-02). Proposals `[0, 0, 100]`, k = 2, n = 3.

| Variant | Filter | Result on the one-row toy table |
|---|---|---|
| proposals 1 and 2 | `sale_date > '2026-01-01' AND sale_date < '2026-01-02'` | 0 |
| proposal 3 | `sale_date >= '2026-01-01' AND sale_date < '2026-01-02'` | 100 |

Quorum 2-of-3 → `{"consensus": true, "value": 0, "votes": 2}`; independent reference (Python on the
interval) = 100: **wrong consensus**. The strict `>` drops the rows exactly on the inclusive lower bound.
Check: a boundary probe (count rows equal to the lower bound: 1), which refutes 0.

## Consequence for the panel and the checking

1. Agreement is an absence of disagreement, not a proof (CM2). Our fixed panel was not caught on our data,
   but swapping one member for a cheaper one (WC-1) or for a free one (WC-2, WC-3) produces a wrong
   consensus on the same traces. The choice of panel is part of the risk.
2. Shared errors have recognisable shapes: an **empty result read as 0** (WC-1, WC-2, DEMO-VOTE) and a
   **shared convention error** (WC-3). Each has a cheap deterministic check: the non-empty probe, the
   boundary probe, the decomposition of the age condition. They are written into the routing rule.
3. Where only one family is right (C10, C15 C17 C19), a quorum cannot confirm the correct answer. The
   check there is an independent reference, whose cost is evaluated in TD 3.
