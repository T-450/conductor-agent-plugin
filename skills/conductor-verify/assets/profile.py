#!/usr/bin/env python3
"""Tier profiler (SPEC-verify-strategy): pure function, stdlib only.

profile_item(state, deps, hw, blast) -> (tier, total).
  hw == 2 -> T4 (physical-only short-circuits the sum).
  else sum: 0 -> T0; 1-2 -> T1; 3-5 -> T2; 6+ -> T3.
`--check` loads gold_fixtures.json and asserts exact tier match.
"""

import json
import sys
from pathlib import Path

PROFILER_VERSION = "1.0.0-provisional"


def profile_item(state: int, deps: int, hw: int, blast: int):
    for v in (state, deps, hw, blast):
        assert v in (0, 1, 2), f"axis out of range: {v}"
    if hw == 2:
        return "T4", state + deps + hw + blast
    total = state + deps + hw + blast
    if total == 0:
        return "T0", total
    if total <= 2:
        return "T1", total
    if total <= 5:
        return "T2", total
    return "T3", total


def main() -> int:
    gold = json.loads((Path(__file__).resolve().parent / "gold_fixtures.json").read_text())
    hits = 0
    for fx in gold["fixtures"]:
        got, total = profile_item(*[fx[k] for k in ("state", "deps", "hw", "blast")])
        mark = "OK" if got == fx["tier"] else "MISMATCH"
        if got == fx["tier"]:
            hits += 1
        print(f"fixture: {fx['name']} expected={fx['tier']} got={got} total={total} -> {mark}")
    print(f"TIER-MATCH: {hits}/{len(gold['fixtures'])}")
    return 0 if hits == len(gold["fixtures"]) else 1


if __name__ == "__main__":
    sys.exit(main())
