#!/usr/bin/env python3
"""TD 2 step 3: the kit's routing simulator, adapted to the GRP2 routing rule.

Same interface as the kit's `atelier-routage.py` (RESOURCES, choose, scenarios,
--scenario), standard library only, no API call, no key.

What changed from the kit version (see td2/C-routing/routing-rule.md):
  - RESOURCES are our five TD 1 models, each on the route we actually used
    (free plan / :free route, cash 0) and, for the Groq models, the usage-billed
    route of the SAME model (Groq Developer), priced from the portfolio.
  - "level" is replaced by the set of question families on which the model is
    eligible, COMPUTED from td1/traces-td1.csv at start-up (review A, step 3):
    `--criterion base` (default, the rule): every base-batch cell of the family
    correct; `--criterion every-run`: every cell correct in every run of the model.
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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "td2"))
from common import FAMILIES, TRACES_ALL, family_scores, question_families, read_csv  # noqa: E402

# Paid-equivalent cost of ONE request on the usage-billed route of the same model:
# mean tokens of the successful base-batch answers of td1/traces-td1.csv x Groq prices
# of methode-cout-en.md step 2 (checked 2026-10-05), USD excl. tax per million tokens.
# The tokens and the latency are MEASURED here from the traces (review B, step 3); they
# used to be copied by hand (641/286 ...) and would silently go stale with new traces.
PRICES = {"gpt-oss-20b": (0.075, 0.30), "gpt-oss-120b": (0.15, 0.60), "qwen3.8-27b": (0.80, 4.00)}


def _measure():
    tokens, latency = {}, {}
    rows = [r for r in read_csv(TRACES_ALL) if r["in_base_batch"] == "yes" and r["http_status"] == "200"]
    for model in {r["model_requested"] for r in rows}:
        mine = [r for r in rows if r["model_requested"] == model]
        name = model.split("/")[-1]
        tokens[name] = (round(sum(int(r["tokens_prompt"]) for r in mine) / len(mine)),
                        round(sum(int(r["tokens_completion"]) for r in mine) / len(mine)))
        latency[model] = round(sum(float(r["latency_ms"]) for r in mine) / len(mine))
    return tokens, latency


TOKENS, LATENCY_MS = _measure()


def per_request(model):
    """USD per request; TOKENS keys are short names (gpt-oss-20b), PRICES has the same keys."""
    (t_in, t_out), (p_in, p_out) = TOKENS[model], PRICES[model]
    return round((t_in * p_in + t_out * p_out) / 1e6, 6)


SCORES = family_scores(read_csv(TRACES_ALL), question_families())


def eligible_families(model, criterion):
    """Families on which `model` (provider-less id) is eligible under the criterion."""
    out = set()
    for fam in FAMILIES:
        sc = SCORES[(model, fam)]
        if criterion == "base":
            ok = sc["base"][1] == sc["base"][2]
        elif criterion == "every-run":
            ok = all(correct == total for _, correct, total in sc["runs"])
        else:
            raise ValueError(f"unknown criterion {criterion!r}")
        if ok:
            out.add(fam)
    return out


def evidence(model, family):
    """Readable TD 1 evidence for one model on one family, generated from the traces."""
    sc = SCORES[(model, family)]
    run, correct, total = sc["base"]
    others = ", ".join(f"{r} {c}/{t}" for r, c, t in sc["runs"] if r != run)
    return (f"{model.split('/')[-1]} on {family}: base {correct}/{total} ({run})"
            + (f"; other runs {others}" if others else ""))


# Routes we used (cash 0) and the usage-billed route of the same Groq models.
# price_rank: portfolio price per million output tokens of the model (0 for :free routes,
# which have no paid route), used to order the included routes by cost.
ROUTES = [
    ("north-mini-code:free", "openrouter", "cohere/north-mini-code:free", "free", 0.0, 0.0),
    ("dots-3-note:free", "openrouter", "dots-studio/dots-3-note-preview:free", "free", 0.0, 0.0),
    ("gpt-oss-20b:groq-free", "groq", "openai/gpt-oss-20b", "free", 0.0, 0.30),
    ("gpt-oss-120b:groq-free", "groq", "openai/gpt-oss-120b", "free", 0.0, 0.60),
    ("qwen3.8-27b:groq-free", "groq", "qwen/qwen3.8-27b", "free", 0.0, 4.00),
    ("gpt-oss-20b:groq-developer", "groq", "openai/gpt-oss-20b", "tokens", per_request("gpt-oss-20b"), 0.30),
    ("gpt-oss-120b:groq-developer", "groq", "openai/gpt-oss-120b", "tokens", per_request("gpt-oss-120b"), 0.60),
    ("qwen3.8-27b:groq-developer", "groq", "qwen/qwen3.8-27b", "tokens", per_request("qwen3.8-27b"), 4.00),
]


def build_resources(criterion="base"):
    return [{"id": rid, "model": f"{provider}:{model}", "access": access, "available": True, "cash": cash,
             "price_rank": rank, "latency_ms": LATENCY_MS[model], "reset_minutes": None,
             "families": eligible_families(model, criterion)}
            for rid, provider, model, access, cash, rank in ROUTES]


RESOURCES = build_resources("base")

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
        # A member counts for the quorum only if it is available AND eligible on the family:
        # north-mini-code is in the panel but 0/4 on completed age, its vote cannot confirm a value.
        def usable(m):
            return any(r["model"] == m and r["available"] and r["cash"] == 0 and family in r["families"]
                       for r in resources)
        up = [m for m in PANEL if usable(m)]
        dead = [m.split("/")[-1] for m in PANEL if m not in up]
        note = (f"panel members available and eligible on '{family}': {len(up)}/3"
                + (f" (not counted: {', '.join(dead)})" if dead else "")
                + "; an unavailable member stays in n")
        if len(up) < 2:
            check = f"{REF} (quorum cannot confirm: fewer than k = 2 usable members)" + (
                f"; {REVIEW}" if use == "payout" else "")
        elif len(up) == 2:
            note += "; no failure tolerated: both usable members must agree"
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
    ruled_out = [f"{r['id']}: not eligible ({evidence(r['model'].split(':', 1)[1], family)})"
                 for r in resources if family not in r["families"]]
    base = {"checks": checks, "check_note": note}

    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    ruled_out += [f"{r['id']}: unavailable" for r in eligible if not r["available"]]
    if included:
        chosen = min(included, key=lambda r: (r["price_rank"], r["latency_ms"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, **base, "ruled_out": ruled_out,
                "reason": f"cheapest included route eligible on '{family}' "
                          f"({evidence(chosen['model'].split(':', 1)[1], family)})"}

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
                          f"{chosen['cash']} USD per request within the budget "
                          f"({evidence(chosen['model'].split(':', 1)[1], family)})"}

    return {"action": "abstain", "resource": None, "cash": 0, **base, "ruled_out": ruled_out,
            "reason": f"no model correct on '{family}' in TD 1 is available within the deadline and budget; "
                      "the cheaper available models are not used because they failed this family"}


def scenarios(resources=None):
    global RESOURCES
    RESOURCES = resources or RESOURCES
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
    parser.add_argument("--criterion", choices=["base", "every-run"], default="base",
                        help="eligibility: every base-batch cell (default) or every cell of every run")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios(build_resources(args.criterion)):
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "criterion": args.criterion,
                          "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
