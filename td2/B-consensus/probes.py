"""Deterministic probes that refute a wrong 0 without any model (TD 2 review of step 2).

The reference query of a question is re-executed read-only through the kit's
sandbox, with its SELECT list replaced:
  - COUNT(*)                          -> order lines of the population;
  - MIN(o.quantity_product * p.price) -> smallest line amount (> 0 means that a
                                         non-empty population cannot sum to 0).
Before this module, the "non-empty check" of explain_wrong_consensus.py counted the
lines in Python and only *asserted* that prices and quantities are positive.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "td2"))
from common import REFERENCE, reference_rows  # noqa: E402
from sandbox_sqlite import execute_query  # noqa: E402

DB = ROOT / "data" / "boutique.sqlite"
SELECT = re.compile(r"^\s*SELECT\s+.*?\s+AS\s+revenue_cents\s+FROM\s", re.IGNORECASE | re.DOTALL)
_REFS = None


def _probe(case, expression):
    global _REFS
    if _REFS is None:
        _REFS = reference_rows(REFERENCE)
    sql = _REFS[case]["sql"]
    if not SELECT.search(sql):
        raise ValueError(f"{case}: reference SQL does not start with 'SELECT ... AS revenue_cents FROM'")
    result = execute_query(DB, SELECT.sub(f"SELECT {expression} AS revenue_cents FROM ", sql, count=1))
    if not result["ok"]:
        raise ValueError(f"{case}: probe failed: {result['reason']} {result['detail']}")
    return result["value"]


def population_lines(case):
    """Number of order lines selected by the reference query of `case`."""
    return _probe(case, "COUNT(*)")


def smallest_line_amount(case):
    """Smallest quantity x price among those lines (None when the population is empty)."""
    return _probe(case, "MIN(o.quantity_product * p.price)")
