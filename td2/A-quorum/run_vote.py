#!/usr/bin/env python3
"""TD 2 step 1 driver: run `atelier-vote.py` on the twenty questions of ONE experiment.

Standard library only, no network. For each case C01..C20 it runs, unchanged,

    python atelier-vote.py --traces <file> --case <Cxx>

from the repository root, keeps the JSON line it prints (raw evidence), and adds
the value each panel member proposed (read with the workshop's own
`proposals_for`, so the same "last attempt per member" selection) to make the
table readable. The reference is only used AFTER the decision, by the workshop.

    python td2/A-quorum/run_vote.py --traces traces-td1-base.csv --label base
    python td2/A-quorum/run_vote.py --traces traces-raw/traces-td1_full.csv --label full1

One file = one experiment: `atelier-vote.py` takes the last row per panel member,
so a file that mixes runs (such as `traces-td1.csv`) must not be used here.
"""
import argparse
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "results"
CASES = [f"C{i:02d}" for i in range(1, 21)]
SHORT = {"openai/gpt-oss-120b": "gpt-oss-120b", "cohere/north-mini-code:free": "north-mini-code",
         "qwen/qwen3.8-27b": "qwen3.8-27b"}


def load_workshop():
    spec = importlib.util.spec_from_file_location("atelier_vote", ROOT / "atelier-vote.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--traces", required=True, help="trace CSV of one experiment, relative to the repo root")
    parser.add_argument("--label", required=True, help="suffix of the output files")
    args = parser.parse_args()

    workshop = load_workshop()
    with (ROOT / args.traces).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    OUT.mkdir(exist_ok=True)
    raw_lines, table = [], []
    for case in CASES:
        proc = subprocess.run([sys.executable, "atelier-vote.py", "--traces", args.traces, "--case", case],
                              cwd=ROOT, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise SystemExit(f"{case}: atelier-vote.py failed: {proc.stderr.strip()}")
        line = proc.stdout.strip()
        raw_lines.append(line)
        out = json.loads(line)
        decision = out["decision"]
        members = workshop.proposals_for(rows, case, "real")
        proposed = {SHORT[p.model_requested]: ("unavailable" if p.value is None else p.value) for p in members}
        if decision["consensus"]:
            agreement = "yes" if out["matches_reference"] else "NO (wrong consensus)"
        else:
            agreement = "n/a (abstention)"
        table.append({
            "case_id": case,
            "gpt-oss-120b": proposed["gpt-oss-120b"],
            "north-mini-code": proposed["north-mini-code"],
            "qwen3.8-27b": proposed["qwen3.8-27b"],
            "decision": "consensus" if decision["consensus"] else "abstention",
            "value": "" if decision["value"] is None else decision["value"],
            "votes": f'{decision["votes"]}/3',
            "agreeing_models": " ".join(m.split(":", 1)[1] for m in decision["models"]),
            "reference": out["reference"],
            "agrees_with_reference": agreement,
        })

    (OUT / f"vote-{args.label}.jsonl").write_text("\n".join(raw_lines) + "\n", encoding="utf-8")
    with (OUT / f"vote-{args.label}.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)

    cols = list(table[0])
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for row in table:
        print("| " + " | ".join(str(row[c]) for c in cols) + " |")
    n_cons = sum(r["decision"] == "consensus" for r in table)
    n_ok = sum(r["agrees_with_reference"] == "yes" for r in table)
    n_wrong = sum(r["agrees_with_reference"].startswith("NO") for r in table)
    print(f"\n{args.traces}: {n_cons} consensus ({n_ok} equal to the reference, {n_wrong} wrong), "
          f"{20 - n_cons} abstentions, panel 2-of-3")


if __name__ == "__main__":
    main()
