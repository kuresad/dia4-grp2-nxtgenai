#!/usr/bin/env python3
"""TD 2 step 3: the kit's routing simulator, adapted to the GRP2 routing rule.

Same interface as the kit's `atelier-routage.py` (RESOURCES, choose, scenarios,
--scenario), standard library only, no API call, no key.

What changed from the kit version (see td2/C-routing/routing-rule.md):
  - RESOURCES are our five TD 1 models, each on the route we actually used
    (free plan / :free route, cash 0) and, for the Groq models, the usage-billed
    route of the SAME model (Groq Developer), priced from the portfolio.
  - "level" is replaced by the set of question families on which the model was
    correct on every base-batch cell in TD 1 (td2/C-routing/results/family-evidence.md).
  - a request is read as (family, use, deadline, budget); the use (internal
    dashboard, figure shown to the customer, amount paid out) sets the checking.
  - the decision carries the panel of the quorum, the resources ruled out and
    a reason that cites the TD 1 cells.

The availability values of the scenarios are ASSUMPTIONS (nature = simulation):
they are not measured from a provider. The capabilities and prices are not
fictitious: they come from TD 1 and from the portfolio.
"""
import argparse
import json

# Paid-equivalent cost of ONE request on the usage-billed route of the same model:
# mean base-batch tokens of traces-td1.csv (in_base_batch = yes) x Groq prices of
# methode-cout-en.md step 2 (checked 2026-10-05), USD excl. tax.
#   gpt-oss-20b : 641 in x 0.075 + 286 out x 0.30 per million -> 0.000134
#   gpt-oss-120b: 641 in x 0.15  + 259 out x 0.60 per million -> 0.000252
#   qwen3.8-27b : 630 in x 0.80  + 138 out x 4.00 per million -> 0.001056
TOKENS = {"gpt-oss-20b": (641, 286), "gpt-oss-120b": (641, 259), "qwen3.8-27b": (630, 138)}
PRICES = {"gpt-oss-20b": (0.075, 0.30), "gpt-oss-120b": (0.15, 0.60), "qwen3.8-27b": (0.80, 4.00)}


def per_request(model):
    (t_in, t_out), (p_in, p_out) = TOKENS[model], PRICES[model]
    return round((t_in * p_in + t_out * p_out) / 1e6, 6)


ALL = {"period", "completed age at a date", "age at the order", "product list", "combinations"}
SIMPLE = {"period", "product list"}

# families: base-batch cells all correct in TD 1 (family-evidence.md, "base batch" column).
# price_rank: portfolio price per million output tokens of the model (0 for :free routes,
# which have no paid route), used to order the included routes by cost.
RESOURCES = [
    {"id": "north-mini-code:free", "model": "openrouter:cohere/north-mini-code:free", "family": "cohere",
     "families": SIMPLE, "access": "free", "available": True, "cash": 0.0, "price_rank": 0.0,
     "latency_ms": 1930, "reset_minutes": None,
     "evidence": "period 6/6 and product 4/4 in C-jason-1 and FULL-1; age 0/5, combinations 0/5 (base)"},
    {"id": "dots-3-note:free", "model": "openrouter:dots-studio/dots-3-note-preview:free", "family": "dots",
     "families": SIMPLE, "access": "free", "available": True, "cash": 0.0, "price_rank": 0.0,
     "latency_ms": 3482, "reset_minutes": None,
     "evidence": "period 6/6 and product 4/4 in FULL-1 and E-jason-1; dots:C08 C11 C10 C15 C17 C18 wrong (base)"},
    {"id": "gpt-oss-20b:groq-free", "model": "groq:openai/gpt-oss-20b", "family": "gpt-oss",
     "families": ALL, "access": "free", "available": True, "cash": 0.0, "price_rank": 0.30,
     "latency_ms": 825, "reset_minutes": None,
     "evidence": "20/20 in B-1 (base); FULL-1 18/20: gpt-oss-20b:C02 and C11 wrong in that repetition"},
    {"id": "gpt-oss-120b:groq-free", "model": "groq:openai/gpt-oss-120b", "family": "gpt-oss",
     "families": ALL - {"combinations"}, "access": "free", "available": True, "cash": 0.0, "price_rank": 0.60,
     "latency_ms": 961, "reset_minutes": None,
     "evidence": "18/20 in A-jason-1 (base): gpt-oss-120b:C15 C19 wrong; 20/20 in FULL-1, A-op2-1, A-jason-2"},
    {"id": "qwen3.8-27b:groq-free", "model": "groq:qwen/qwen3.8-27b", "family": "qwen",
     "families": SIMPLE | {"completed age at a date"}, "access": "free", "available": True, "cash": 0.0,
     "price_rank": 4.00, "latency_ms": 516, "reset_minutes": None,
     "evidence": "16/20 in D-kuresa-1 (base): qwen3.8-27b:C10 C15 C17 C19 wrong; C09 wrong in 3 of 5 runs"},
    {"id": "gpt-oss-20b:groq-developer", "model": "groq:openai/gpt-oss-20b", "family": "gpt-oss",
     "families": ALL, "access": "tokens", "available": True, "cash": per_request("gpt-oss-20b"),
     "price_rank": 0.30, "latency_ms": 825, "reset_minutes": None,
     "evidence": "same model as gpt-oss-20b:groq-free, usage-billed Groq Developer route"},
    {"id": "gpt-oss-120b:groq-developer", "model": "groq:openai/gpt-oss-120b", "family": "gpt-oss",
     "families": ALL - {"combinations"}, "access": "tokens", "available": True,
     "cash": per_request("gpt-oss-120b"), "price_rank": 0.60, "latency_ms": 961, "reset_minutes": None,
     "evidence": "same model as gpt-oss-120b:groq-free, usage-billed Groq Developer route"},
    {"id": "qwen3.8-27b:groq-developer", "model": "groq:qwen/qwen3.8-27b", "family": "qwen",
     "families": SIMPLE | {"completed age at a date"}, "access": "tokens", "available": True,
     "cash": per_request("qwen3.8-27b"), "price_rank": 4.00, "latency_ms": 516, "reset_minutes": None,
     "evidence": "same model as qwen3.8-27b:groq-free, usage-billed Groq Developer route"},
]

# The fixed three-family panel of TD 2 (one model per family, k = 2 of n = 3).
PANEL = ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free", "groq:qwen/qwen3.8-27b"]

# Checking per (family, use). The cost of an error grows from left to right.
QUORUM = "2-of-3 quorum on the fixed panel; abstention escalates to the reference"
REF = "independent reference query by a member, compared with the value"
REVIEW = "human review before payment"
CHECKS = {
    "period": {"dashboard": "none (read-only execution, integer value)",
               "customer": QUORUM, "payout": f"{QUORUM}; {REF}; {REVIEW}"},
    "product list": {"dashboard": "none (read-only execution, integer value)",
                     "customer": QUORUM, "payout": f"{QUORUM}; {REF}; {REVIEW}"},
    "completed age at a date": {"dashboard": "non-empty check: a 0 is refused if the age filter alone matches rows",
                                "customer": QUORUM, "payout": f"{QUORUM}; {REF}; {REVIEW}"},
    "age at the order": {"dashboard": "non-empty check: a 0 is refused if the age filter alone matches rows",
                         "customer": REF, "payout": f"{REF}; {REVIEW}"},
    "combinations": {"dashboard": "bound check: the value cannot exceed the same query without its age or product filter",
                     "customer": REF, "payout": f"{REF}; {REVIEW}"},
}
WHY_CHECK = {
    "age at the order": "no 2-of-3 panel of distinct families is right on C10 (only gpt-oss is); "
                        "qwen3.8-27b and dots-3-note share the wrong value 119410 (case WC-3)",
    "combinations": "the fixed panel abstains on C15 C17 C19 in both the base batch and FULL-1; "
                    "only gpt-oss-20b is 5/5 (base)",
}


def checks_for(request, resources):
    family, use = request["family"], request["use"]
    check = CHECKS[family][use]
    note = WHY_CHECK.get(family, "")
    if check.startswith("2-of-3"):
        up = [m for m in PANEL if any(r["model"] == m and r["available"] and r["cash"] == 0 for r in resources)]
        note = f"panel available {len(up)}/3 (an unavailable member stays in n)"
        if len(up) < 2:
            check = f"{REF} (quorum impossible: fewer than k = 2 members available)" + (
                f"; {REVIEW}" if use == "payout" else "")
    return check, note


def choose(request, resources):
    """A deterministic routing policy, with a reason someone outside the group can read.

    Order of use (CM2): included capacity of an eligible model, cheapest first;
    wait for the refill if the request can wait; paid route of an eligible model
    within the budget; otherwise abstain. A refill time does not prove
    availability: it is measured again at wake-up.
    """
    family = request["family"]
    if family not in CHECKS:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": "none", "ruled_out": [],
                "reason": f"family '{family}' was not measured in TD 1: no model is known to be correct on it; "
                          "answer only after a TD 1-style measurement"}
    checks, note = checks_for(request, resources)
    eligible = [r for r in resources if family in r["families"]]
    ruled_out = [f"{r['id']}: not correct on every '{family}' cell in TD 1 ({r['evidence']})"
                 for r in resources if family not in r["families"]]
    base = {"checks": checks, "check_note": note}

    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    ruled_out += [f"{r['id']}: unavailable" for r in eligible if not r["available"]]
    if included:
        chosen = min(included, key=lambda r: (r["price_rank"], r["latency_ms"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, **base, "ruled_out": ruled_out,
                "reason": f"cheapest included route correct on '{family}' in TD 1 ({chosen['evidence']})"}

    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0 and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], r["price_rank"]))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, **base, "ruled_out": ruled_out,
                "wake_in_minutes": chosen["reset_minutes"],
                "reason": f"free quota of an eligible model refills in {chosen['reset_minutes']} min, within the "
                          f"{request['deadline_minutes']} min deadline: wait, then measure availability again"}

    paid = [r for r in eligible if r["available"] and 0 < r["cash"] <= request["budget"]]
    ruled_out += [f"{r['id']}: {r['cash']} USD exceeds the budget {request['budget']}"
                  for r in eligible if r["available"] and r["cash"] > request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], **base, "ruled_out": ruled_out,
                "reason": f"no included capacity in time; usage-billed route of an eligible model, "
                          f"{chosen['cash']} USD per request within the budget ({chosen['evidence']})"}

    return {"action": "abstain", "resource": None, "cash": 0, **base, "ruled_out": ruled_out,
            "reason": f"no model correct on '{family}' in TD 1 is available within the deadline and budget; "
                      "the cheaper available models are not used because they failed this family"}


def scenarios():
    base = {"family": "period", "use": "dashboard", "can_wait": True, "deadline_minutes": 120, "budget": 0.01}
    groq_exhausted = [dict(r, available=False, reset_minutes=60) if r["id"].endswith("groq-free") else dict(r)
                      for r in RESOURCES]
    north_down = [dict(r, available=False) if r["id"] == "north-mini-code:free" else dict(r) for r in RESOURCES]
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "combinations"}, RESOURCES),
        ("deferrable", {**base, "family": "combinations"}, groq_exhausted),
        ("urgent", {**base, "family": "combinations", "use": "customer", "can_wait": False,
                    "deadline_minutes": 5}, groq_exhausted),
        ("budget exhausted", {**base, "family": "combinations", "use": "customer", "can_wait": False,
                              "budget": 0}, groq_exhausted),
        ("high impact", {**base, "family": "completed age at a date", "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "refund rate"}, RESOURCES),
        # Extra scenario (template line R2): preferred provider unavailable.
        ("preferred unavailable", {**base, "family": "product list", "use": "customer", "can_wait": False,
                                   "deadline_minutes": 5}, north_down),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
