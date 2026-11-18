#!/usr/bin/env python3
"""TD 2 step 1: contract tests of `Orchestrateur.vote_k_sur_n`, written to voting-tests-en.csv.

Standard library only, no network. Synthetic values in cents (nature = simulation),
except T11, which replays the stored trace of run FULL-1 on C09 (nature = real).

    python td2/A-quorum/test_vote.py
"""
import csv
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

sys.path.insert(0, str(ROOT / "td2"))
from common import load_vote, proposal_from_row, read_csv  # noqa: E402

vote = load_vote()

A = ("groq", "openai/gpt-oss-120b")
B = ("openrouter", "cohere/north-mini-code:free")
C = ("groq", "qwen/qwen3.8-27b")
D = ("groq", "openai/gpt-oss-20b")
E = ("openrouter", "dots-studio/dots-3-note-preview:free")
PANEL3 = [A, B, C]
PANEL5 = [A, B, C, D, E]


def P(route, value, verdict=None):
    return SimpleNamespace(provider=route[0], model_requested=route[1], value=value,
                           verdict=verdict or ("executed" if value is not None else "error"))


def short(route):
    return route[1].split("/")[-1]


# test_id, description, panel, values, k, expected (dict or "ValueError")
CASES = [
    ("T01", "agreement 3/3", PANEL3, [100, 100, 100], 2, {"consensus": True, "value": 100, "votes": 3, "models": ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free", "groq:qwen/qwen3.8-27b"]}),
    ("T02", "agreement 2/3", PANEL3, [100, 100, 120], 2, {"consensus": True, "value": 100, "votes": 2, "models": ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free"]}),
    ("T03", "disagreement: three different values", PANEL3, [100, 110, 120], 2, {"consensus": False, "value": None, "votes": 1}),
    ("T04", "one unavailable, the two others agree", PANEL3, [100, None, 100], 2, {"consensus": True, "value": 100, "votes": 2, "models": ["groq:openai/gpt-oss-120b", "groq:qwen/qwen3.8-27b"]}),
    ("T05", "one unavailable, the two others disagree: n stays 3", PANEL3, [100, None, 120], 2, {"consensus": False, "value": None, "votes": 1}),
    ("T06", "two unavailable: 1 vote < k, abstain (n stays 3)", PANEL3, [100, None, None], 2, {"consensus": False, "value": None, "votes": 1}),
    ("T07", "all unavailable", PANEL3, [None, None, None], 2, {"consensus": False, "value": None, "votes": 0}),
    ("T08", "duplicate route (same provider and model twice)", [A, A, C], [100, 100, 120], 2, "ValueError"),
    ("T09", "k=1 is not a strict majority of 3", PANEL3, [100, 110, 120], 1, "ValueError"),
    ("T10", "k=4 > n=3", PANEL3, [100, 100, 100], 4, "ValueError"),
    ("T12", "3-of-5: three agree", PANEL5, [100, 100, None, 100, 90], 3, {"consensus": True, "value": 100, "votes": 3, "models": ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free", "groq:openai/gpt-oss-20b"]}),
    ("T13", "3-of-5: only two agree, two unavailable", PANEL5, [100, 100, None, None, 90], 3, {"consensus": False, "value": None, "votes": 2}),
    ("T14", "2-of-5 refused (5 // 2 = 2)", PANEL5, [100, 100, 1, 2, 3], 2, "ValueError"),
    ("T15", "wrong consensus is kept: the vote does not know the reference (100)", PANEL3, [0, 0, 100], 2, {"consensus": True, "value": 0, "votes": 2, "models": ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free"]}),
    ("T16", "value 0 is a vote, not a missing value", PANEL3, [0, None, 0], 2, {"consensus": True, "value": 0, "votes": 2, "models": ["groq:openai/gpt-oss-120b", "groq:qwen/qwen3.8-27b"]}),
    ("T17", "raw trace verdict 'correct' passed by mistake is refused, not silently ignored", PANEL3,
     [100, 100, 100], 2, "ValueError", {"verdict": "correct"}),
    ("T18", "distinct_families=True: gpt-oss-20b and gpt-oss-120b are one family", [A, D, C],
     [100, 100, 120], 2, "ValueError", {"distinct_families": True}),
    ("T19", "same panel without the option: the contract only refuses identical routes", [A, D, C],
     [100, 100, 120], 2, {"consensus": True, "value": 100, "votes": 2}),
]


def real_c09_full1():
    """T11: FULL-1, C09: north-mini-code returned sql_invalid (no value) -> unavailable member."""
    rows = read_csv(ROOT / "td1/traces-raw/traces-td1_full.csv")
    last = {}
    for r in rows:
        if r["case_id"] == "C09":
            last[(r["provider"], r["model_requested"])] = r
    return [proposal_from_row(last[route]).value for route in PANEL3]


def main():
    c09 = real_c09_full1()
    CASES.insert(10, ("T11", "real trace FULL-1 C09: north-mini-code sql_invalid, 120b and qwen disagree",
                      PANEL3, c09, 2, {"consensus": False, "value": None, "votes": 1}))
    out_rows, failures = [], 0
    for test_id, description, panel, values, k, expected, *extra in CASES:
        options = dict(extra[0]) if extra else {}
        verdict = options.pop("verdict", None)
        try:
            result = vote([P(r, v, verdict) for r, v in zip(panel, values)], k, **options)
            actual = json.dumps(result)
            ok = expected != "ValueError" and all(result[key] == val for key, val in expected.items())
        except ValueError as exc:
            result, actual = None, f"ValueError: {exc}"
            ok = expected == "ValueError"
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'} {test_id} {description}: {actual}")
        out_rows.append({
            "test_id": test_id,
            "nature": "real (td1/traces-raw/traces-td1_full.csv, run FULL-1)" if test_id == "T11" else "simulation",
            "panel": " ".join(f"{r[0]}:{r[1]}" for r in panel),
            "fixed_n": len(panel),
            "k": k,
            "input_values": " ".join("unavailable" if v is None else str(v) for v in values),
            "unavailable_members": " ".join(short(r) for r, v in zip(panel, values) if v is None) or "none",
            "expected_result_or_abstention": expected if expected == "ValueError" else json.dumps(expected),
            "actual_result": actual,
            "agreeing_members": " ".join(m.split("/")[-1] for m in result["models"]) if result and result["models"] else "none",
            "evidence_file": "td2/A-quorum/results/test-vote.txt",
        })
    with (HERE / "voting-tests-en.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out_rows[0]))
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"\n{len(CASES) - failures}/{len(CASES)} tests pass")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
