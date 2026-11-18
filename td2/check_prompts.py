#!/usr/bin/env python3
"""TD 2: check that the prompts are unchanged since TD 1 (no network).

Rebuilds, with the skeleton's own `build_prompt`, the prompt of each of the twenty
questions and compares its SHA-256 with the `prompt_sha256` of every row of
`td1/traces-td1.csv`.

    python td2/check_prompts.py
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skeleton
spec.loader.exec_module(skeleton)

schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
questions = json.loads((ROOT / "questions-td1.json").read_text(encoding="utf-8"))["questions"]
expected = {q["id"]: skeleton.build_prompt(schema, q["question"])[2] for q in questions}
rows = list(csv.DictReader((ROOT / "td1" / "traces-td1.csv").open(encoding="utf-8", newline="")))
mismatch = [(r["run_id"], r["model_requested"], r["case_id"]) for r in rows
            if r["prompt_sha256"] != expected[r["case_id"]]]
print(f"{len(rows)} trace rows, {len(expected)} prompts rebuilt from skeleton-multi-llm-en.py; "
      f"{len(rows) - len(mismatch)} match, {len(mismatch)} differ")
for m in mismatch[:20]:
    print("differs:", *m)
