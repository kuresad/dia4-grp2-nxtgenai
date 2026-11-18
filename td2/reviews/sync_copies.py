#!/usr/bin/env python3
"""Copy the two reviews of each step into that step's folder (td2/<step>/reviews/).

td2/reviews/ is the reference; never edit a copy by hand, run this script instead:

    python td2/reviews/sync_copies.py

Links are rewritten so that they still resolve one folder deeper: a relative link
that leaves td2/reviews/ ("../...") gets one more "../"; links between the two
reviews of a step stay as they are (both are copied side by side).
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = {"etape1": "A-quorum", "etape2": "B-consensus", "etape3": "C-routing"}
LINK = re.compile(r"\]\((\.\./[^)]*)\)")


def main():
    for review in sorted(HERE.glob("revue-*-etape*.md")):
        step = STEPS[review.stem.split("-")[-1]]
        target = HERE.parent / step / "reviews" / review.name
        target.parent.mkdir(exist_ok=True)
        text = LINK.sub(lambda m: f"](../{m.group(1)})", review.read_text(encoding="utf-8"))
        header = (f"<!-- Copie générée par td2/reviews/sync_copies.py depuis td2/reviews/{review.name}. "
                  "Ne pas modifier ici. -->\n")
        target.write_text(header + text, encoding="utf-8", newline="\n")
        print(f"{review.relative_to(HERE.parent.parent)} -> {target.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()
