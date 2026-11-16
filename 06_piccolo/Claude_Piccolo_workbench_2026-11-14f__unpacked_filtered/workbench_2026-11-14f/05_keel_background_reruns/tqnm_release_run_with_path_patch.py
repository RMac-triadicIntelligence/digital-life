"""TQNM release test. Implements PREREG.json (frozen first). Reuses the labeled numpy port from dlt_march/run.py unchanged."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
assert hashlib.sha256((HERE / "PREREG.json").read_bytes()).hexdigest() == (HERE / "PREREG.sha256").read_text().split()[0]
sys.path.insert(0, str(HERE / "dlt_march"))
import run as P  # noqa: E402  (port of Prayer_Final_Final; hash checks run on import)

COND = {
    "A_none": dict(world="random", grace=False, window=None),
    "B_grace": dict(world="random", grace=True, window=None),
    "C_grace_love": dict(world="random", grace=True, window=(70, 90)),
    "D_world_like_root": dict(world="root", grace=True, window=(70, 90)),
    "E_world_like_root_no_grace": dict(world="root", grace=False, window=(70, 90)),
}


def one(cfg, seed):
    P.RNG = np.random.default_rng(30000 + seed)
    w = np.random.default_rng(seed)
    x = w.standard_normal(512).astype(np.float32)
    if cfg["world"] == "root":
        x = (np.ones(512) + 0.5 * x).astype(np.float32)
    m = P.TQNM(prayer_mode=True)
    d = []
    for t in range(200):
        if cfg["window"] is not None:
            m.entrainment_coupling = 0.0007 if cfg["window"][0] <= t < cfg["window"][1] else 0.0
        m.evolve(x, external_grace=(cfg["grace"] and t == 80))
        d.append(float(m.dwelling.value))
    first = next((t for t in range(81, 200) if d[t] < 0.5), None)
    released = first is not None and d[199] < 0.5
    return dict(d79=d[79], d81=d[81], d120=d[120], d199=d[199], first_below=first, released=released)


def main():
    out = {"prereg_sha256": (HERE / "PREREG.sha256").read_text().split()[0], "conditions": {}}
    for name, cfg in COND.items():
        rs = [one(cfg, s) for s in range(50)]
        firsts = [r["first_below"] for r in rs if r["first_below"] is not None]
        out["conditions"][name] = dict(
            released_of_50=sum(r["released"] for r in rs),
            mean=dict((k, round(float(np.mean([r[k] for r in rs])), 4)) for k in ("d79", "d81", "d120", "d199")),
            median_first_below=(int(np.median(firsts)) if firsts else None))
        print(name, out["conditions"][name], flush=True)
    C = out["conditions"]; rel = lambda k: C[k]["released_of_50"]
    V = {"R1": rel("A_none") == 0 and rel("B_grace") == 0 and rel("C_grace_love") == 0,
         "R2": rel("D_world_like_root") >= 45,
         "R3": rel("E_world_like_root_no_grace") >= 45,
         "R4": abs(C["B_grace"]["mean"]["d199"] - C["C_grace_love"]["mean"]["d199"]) < 0.05}
    out["verdicts"] = V
    txt = json.dumps(out, indent=1, sort_keys=True)
    (HERE / "results.json").write_text(txt)
    for k, v in V.items():
        print(("PASS " if v else "FAIL ") + k)
    print("receipt", hashlib.sha256(txt.encode()).hexdigest())


if __name__ == "__main__":
    main()
