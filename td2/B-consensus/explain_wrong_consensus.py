#!/usr/bin/env python3
"""TD 2 step 2: replay the wrong agreements found in the TD 1 traces and check them independently.

Standard library only, no network, no key. Every SQL is read from the stored traces
and re-executed read-only through the kit's `sandbox_sqlite.execute_query`; the
independent check recomputes the value in plain Python from the CSV files, without SQL.

    python td2/B-consensus/explain_wrong_consensus.py

Sections
  1. real batch cases: C02 (run FULL-1), C11 (base batch), C10 (two runs)
  2. independent check: Python recomputation + "non-empty population" test
  3. the quorum each case gives: fixed panel, and panels recomposed from the traces
  4. DEMO-VOTE: the supplied synthetic case, on a one-row toy table
"""
import csv
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "boutique.sqlite"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "td2"))
from sandbox_sqlite import execute_query  # noqa: E402  (kit file, read-only sandbox)
from common import load_vote, proposal_from_row, read_csv, reference_rows  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probes import population_lines, smallest_line_amount  # noqa: E402

VOTE = load_vote()
TRACES = read_csv(ROOT / "td1" / "traces-td1.csv")
REFS = reference_rows(ROOT / "td1" / "reference-td1.csv")


def final_row(model, case, *, run_id=None, base=False):
    """Last attempt of a model on a case, inside one run (or inside the base batch)."""
    rows = [r for r in TRACES if r["model_requested"] == model and r["case_id"] == case
            and (r["run_id"] == run_id if run_id else True) and (r["in_base_batch"] == "yes" if base else True)]
    if not rows:
        raise SystemExit(f"no trace for {model} {case} {run_id or 'base'}")
    return rows[-1]


# ---------------------------------------------------------------------------
# Independent recomputation, plain Python, no SQL
# ---------------------------------------------------------------------------
PRICE = {r["product_id"]: int(r["price"]) for r in csv.DictReader((ROOT / "data/product.csv").open(encoding="utf-8"))}
BIRTH = {r["customer_id"]: date.fromisoformat(r["birth_date"])
         for r in csv.DictReader((ROOT / "data/customers.csv").open(encoding="utf-8")) if r["birth_date"]}
ORDERS = list(csv.DictReader((ROOT / "data/orders.csv").open(encoding="utf-8")))


def completed_age(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def python_revenue(age_on):
    """Sum and number of order lines of customers aged exactly 25 on `age_on(order)`."""
    total = lines = 0
    for o in ORDERS:
        birth = BIRTH.get(o["customer_id"])
        if birth is not None and completed_age(birth, age_on(o)) == 25:
            total += int(o["quantity_product"]) * PRICE[o["product_id"]]
            lines += 1
    return total, lines


def order_day(o):
    return date.fromisoformat(o["date"][:10])


INDEPENDENT = {
    "C02": lambda: python_revenue(lambda o: date(2026, 9, 25)),
    "C11": lambda: python_revenue(lambda o: date(2026, 12, 1)),
    "C10": lambda: python_revenue(order_day),
    "C09": lambda: python_revenue(lambda o: date(2026, 9, 26)),
}


def non_empty_probe(case):
    """Executed on the database (probes.py), no longer asserted: a 0 is impossible if lines > 0 and min > 0."""
    lines, smallest = population_lines(case), smallest_line_amount(case)
    verdict = "a revenue of 0 is impossible" if lines and smallest and smallest > 0 else "0 is possible"
    print(f"  non-empty probe (reference population, read-only SQL): {lines} order lines, "
          f"smallest line amount {smallest} cents -> {verdict}")


def show_case(title, case, members, nature):
    print(f"\n=== {title} ===")
    print(f"nature: {nature}")
    ref = REFS[case]
    ref_exec = execute_query(DB, ref["sql"])["value"]
    py_value, py_lines = INDEPENDENT[case]()
    print(f"reference-td1.csv {case} = {ref['revenue_cents']} (re-executed: {ref_exec}); "
          f"independent Python recomputation = {py_value} over {py_lines} order lines")
    for label, row in members:
        replay = execute_query(DB, row["sql"])
        print(f"- {label}: stored value {row['value']}, verdict {row['verdict']}, "
              f"replayed value {replay['value']} [td1/{row['source_file']}, {row['date_utc']}]")
    return py_value, py_lines


def vote_line(label, members):
    decision = VOTE([proposal_from_row(r) for r in members], 2)
    print(f"  {label}: {json.dumps(decision)}")
    return decision


def main():
    # 1 + 2. Real batch cases --------------------------------------------------
    m120, m20, cohere, qwen, dots = ("openai/gpt-oss-120b", "openai/gpt-oss-20b", "cohere/north-mini-code:free",
                                     "qwen/qwen3.8-27b", "dots-studio/dots-3-note-preview:free")

    full = {m: final_row(m, "C02", run_id="FULL-1") for m in (m120, m20, cohere, qwen, dots)}
    py, lines = show_case("Case WC-1: C02 in run FULL-1 (one run, five models, same prompt)", "C02",
                          [(m, full[m]) for m in (m20, cohere)], "real batch (historical real, stored trace replayed offline)")
    non_empty_probe("C02")
    print("  quorum, 2-of-3:")
    vote_line("declared fixed panel {gpt-oss-120b, north-mini-code, qwen3.8-27b}", [full[m120], full[cohere], full[qwen]])
    vote_line("alternative panel {gpt-oss-20b, north-mini-code, qwen3.8-27b}  (cheapest gpt-oss)", [full[m20], full[cohere], full[qwen]])

    base = {m: final_row(m, "C11", base=True) for m in (m120, m20, cohere, qwen, dots)}
    py, lines = show_case("Case WC-2: C11 in the base batch", "C11",
                          [(m, base[m]) for m in (cohere, dots)], "real batch (base batch = one run per model)")
    non_empty_probe("C11")
    print("  quorum, 2-of-3:")
    vote_line("declared fixed panel {gpt-oss-120b, north-mini-code, qwen3.8-27b}", [base[m120], base[cohere], base[qwen]])
    vote_line("alternative panel {gpt-oss-120b, north-mini-code, dots-3-note}  (both :free OpenRouter models)",
              [base[m120], base[cohere], base[dots]])

    c10 = {"qwen": final_row(qwen, "C10", run_id="D-kuresa-1"), "dots": final_row(dots, "C10", run_id="E-jason-1"),
           "120b": final_row(m120, "C10", run_id="A-jason-1"), "cohere": final_row(cohere, "C10", run_id="C-jason-1")}
    py, lines = show_case("Case WC-3: C10, same NON-ZERO wrong value from two families", "C10",
                          [(f"{qwen} (D-kuresa-1, base)", c10["qwen"]), (f"{dots} (E-jason-1, repetition)", c10["dots"])],
                          "real, but the two values come from two different runs (base D-kuresa-1 and repetition E-jason-1)")
    # Decomposition of the age-at-order population: where do the missing cents go?
    branch_25 = branch_26 = 0
    for o in ORDERS:
        b, d = BIRTH.get(o["customer_id"]), order_day(o)
        if b is None:
            continue
        amount = int(o["quantity_product"]) * PRICE[o["product_id"]]
        passed = (d.month, d.day) >= (b.month, b.day)
        if d.year - b.year == 25 and passed:
            branch_25 += amount
        elif d.year - b.year == 26 and not passed:
            branch_26 += amount
    print(f"  cause check: year difference 25 and birthday reached = {branch_25}; "
          f"year difference 26 and birthday not yet reached = {branch_26}; sum = {branch_25 + branch_26}")
    print("  quorum, 2-of-3:")
    vote_line("declared fixed panel {gpt-oss-120b, north-mini-code, qwen3.8-27b} (base runs)",
              [c10["120b"], c10["cohere"], c10["qwen"]])
    vote_line("panel recomposed across runs {gpt-oss-120b, qwen3.8-27b, dots-3-note} (illustration only)",
              [c10["120b"], c10["qwen"], c10["dots"]])

    c09 = {"cohere": final_row(cohere, "C09", run_id="C-jason-1"), "qwen": final_row(qwen, "C09", run_id="D-kuresa-2"),
           "dots": final_row(dots, "C09", run_id="E-jason-1"), "120b": final_row(m120, "C09", run_id="A-jason-1"),
           "qwen_base": final_row(qwen, "C09", run_id="D-kuresa-1")}
    show_case("Case WC-4: C09, three families on 0, found by scan_shared_errors.py", "C09",
              [(f"{cohere} (C-jason-1, base)", c09["cohere"]), (f"{qwen} (D-kuresa-2, repetition)", c09["qwen"]),
               (f"{dots} (E-jason-1, repetition)", c09["dots"])],
              "real, values from three different runs; qwen3.8-27b returns this 0 in 3 of its 5 runs")
    non_empty_probe("C09")
    print("  quorum, 2-of-3:")
    vote_line("declared fixed panel, base runs (A-jason-1, C-jason-1, D-kuresa-1)",
              [c09["120b"], c09["cohere"], c09["qwen_base"]])
    vote_line("declared fixed panel, qwen from its repetition D-kuresa-2 (illustration)",
              [c09["120b"], c09["cohere"], c09["qwen"]])

    # 4. DEMO-VOTE --------------------------------------------------------------
    print("\n=== DEMO-VOTE (synthetic, supplied by the TD 2 statement; not model output, not the shop data) ===")
    toy = sqlite3.connect(":memory:")
    toy.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
    toy.execute("INSERT INTO sales VALUES ('2026-01-01', 100)")
    strict = "SELECT COALESCE(SUM(amount_cents), 0) FROM sales WHERE sale_date > '2026-01-01' AND sale_date < '2026-01-02'"
    closed = "SELECT COALESCE(SUM(amount_cents), 0) FROM sales WHERE sale_date >= '2026-01-01' AND sale_date < '2026-01-02'"
    v_strict, v_closed = toy.execute(strict).fetchone()[0], toy.execute(closed).fetchone()[0]
    print(f"  variant '>'  (proposals 1 and 2): {strict}\n    -> {v_strict}")
    print(f"  variant '>=' (proposal 3):        {closed}\n    -> {v_closed}")
    reference = sum(a for d, a in [("2026-01-01", 100)] if "2026-01-01" <= d < "2026-01-02")
    print(f"  independent reference (Python, interval [2026-01-01, 2026-01-02)): {reference}")
    panel = [("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"), ("groq", "qwen/qwen3.8-27b")]
    proposals = [SimpleNamespace(provider=p, model_requested=m, value=v, verdict="executed")
                 for (p, m), v in zip(panel, [v_strict, v_strict, v_closed])]
    decision = VOTE(proposals, 2)
    print(f"  quorum 2-of-3 on [{v_strict}, {v_strict}, {v_closed}]: {json.dumps(decision)} "
          f"-> {'WRONG consensus' if decision['value'] != reference else 'correct'}")
    probe = toy.execute("SELECT COUNT(*) FROM sales WHERE sale_date = '2026-01-01'").fetchone()[0]
    print(f"  boundary probe: rows exactly on the lower bound = {probe} -> a '>' filter drops them, the consensus 0 is refuted")


if __name__ == "__main__":
    main()
