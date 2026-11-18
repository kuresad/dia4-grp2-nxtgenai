"""Shared helpers of the TD 2 scripts (standard library only, no network).

Before this module, each script carried its own copy of:
  - the loading of `skeleton-multi-llm-en.py` and of `vote_k_sur_n` (4 copies);
  - the conversion of a trace row into a vote proposal (3 copies, slightly different);
  - the parsing of `reference-td1.csv` (2 copies, one of which assumed a `value`
    column that does not exist: the column is `revenue_cents`).
A change of rule (for example which verdicts carry a vote) had to be made in every
copy. These helpers are now the single place for it.
"""
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]

# Verdicts of the skeleton (Trace.verdict) whose `value` is a result of the SQL.
# Every other verdict (sql_invalid, sql_rejected, access_error, not_executed) is an
# unavailable member: it stays in n and casts no vote.
VOTING_VERDICTS = {"correct", "incorrect"}

_SKELETON = None


def skeleton():
    """The kit's skeleton module, loaded once."""
    global _SKELETON
    if _SKELETON is None:
        spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _SKELETON = module
    return _SKELETON


def load_vote():
    """`vote(proposals, k, **options)`: the group's Orchestrateur.vote_k_sur_n."""
    method = skeleton().Orchestrateur.vote_k_sur_n
    return lambda proposals, k, **options: method(None, proposals, k, **options)


def proposal_from_row(row):
    """One trace row (dict from a trace CSV) -> one vote proposal, as atelier-vote.py builds it."""
    valid = row.get("verdict") in VOTING_VERDICTS and row.get("value") not in (None, "")
    return SimpleNamespace(provider=row["provider"], model_requested=row["model_requested"],
                           value=int(row["value"]) if valid else None,
                           verdict="executed" if valid else "error")


def reference_values(path):
    """{case_id: revenue_cents}, read by the skeleton's own loader (same rules as the scoring)."""
    return skeleton().load_references(Path(path))


def reference_rows(path):
    """{case_id: row} with the reference SQL as well (for re-execution)."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return {r["case_id"]: r for r in csv.DictReader(handle)}


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
