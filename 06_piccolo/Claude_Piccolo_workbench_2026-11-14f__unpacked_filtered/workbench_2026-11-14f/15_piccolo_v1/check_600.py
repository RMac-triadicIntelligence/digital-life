"""PREREG check: at 600 steps the century runner must be October's swarm exactly. Run before any century."""
import json, sys
from pathlib import Path
import commons_century as CC
S = CC.S
stored = json.loads((Path(__file__).resolve().parent / "vendor/commons/commons_v2/results.json").read_text())["per_seed"]
bad = 0; n = 0
for seed in range(20):                       # V2_FULL, all 20 seeds, against October's stored results
    res, _ = CC.run("V2_FULL", seed, 600)
    ok = res == stored["V2_FULL"][seed]; n += 1; bad += (not ok)
    if not ok: print("MISMATCH V2_FULL", seed, res, stored["V2_FULL"][seed])
for variant in S.VARIANTS:                   # the other seven variants, seeds 0..4, against the original function
    if variant == "V2_FULL": continue
    for seed in range(5):
        res, _ = CC.run(variant, seed, 600)
        orig = S.run(variant, seed)
        ok = (res == orig) and (res == stored[variant][seed]); n += 1; bad += (not ok)
        if not ok: print("MISMATCH", variant, seed, res, orig)
# and with the recorder off
for seed in range(3):
    ok = CC.run("V2_FULL", seed, 600, record=False) == stored["V2_FULL"][seed]; n += 1; bad += (not ok)
print(json.dumps({"checks": n, "mismatches": bad, "verdict": "PASS" if bad == 0 else "FAIL"}))
sys.exit(1 if bad else 0)
