"""Supplementary, added after the century was seen: who is alive at 600 steps (October's horizon), by role."""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import commons_century as CC
rows = []
for seed in range(20):
    for T in (600, 2920, 8000):          # day 75 (October's horizon), 1 year, 1,000 days
        if T != 600 and seed >= 10: continue
        res, packed = CC.run("V2_FULL", seed, T)
        al = packed["members_alive"]
        rows.append(dict(seed=seed, ticks=T, day=T // 8, alive=len(al), scouts=sum(1 for m in al if m["scout"]),
                         keepers=sum(1 for m in al if not m["scout"])))
txt = json.dumps(rows, indent=1, sort_keys=True); (HERE / "diag/results_roles.json").write_text(txt)
for T in (600, 2920, 8000):
    r = [x for x in rows if x["ticks"] == T]
    print(T, "seeds", len(r), "keepers alive per seed", [x["keepers"] for x in r], "scouts", [x["scouts"] for x in r])
print("receipt", hashlib.sha256(txt.encode()).hexdigest())
