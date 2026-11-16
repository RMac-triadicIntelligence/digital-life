"""Two diagnostics, both on October's own function (sim_v2.run), not on the century runner.
A. Does grace ever fire? An instrumented COPY of sim_v2.py (two counting lines added, nothing else) is run at
   600 steps on all 20 seeds; its results must still equal October's stored results.
B. Is the century runner still October's swarm PAST 600 steps? October's unedited function is run with its
   module constant STEPS raised to 20,000 and compared with the century runner at 20,000 ticks, seeds 0 and 1.
"""
import hashlib, importlib.util, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import commons_century as CC
S = CC.S
stored = json.loads((HERE / "vendor/commons/commons_v2/results.json").read_text())["per_seed"]["V2_FULL"]

# ---- A
src = (HERE / "vendor/commons/commons_v2/sim_v2.py").read_text()
a = "                a.d, a.run = 0.3, 0\n"
assert src.count(a) == 1
src2 = src.replace(a, a + "                DIAG['grace'] += 1\n")
b = "                a.run += 1; out[\"stuck\"] += 1; continue\n"
assert src2.count(b) == 1
src2 = src2.replace(b, "                a.run += 1; out[\"stuck\"] += 1; DIAG['max_run'] = max(DIAG['max_run'], a.run); continue\n")
src2 = src2.replace("HERE = Path(__file__).resolve().parent\n", f"HERE = Path({str(HERE / 'vendor/commons/commons_v2')!r})\nDIAG = dict(grace=0, max_run=0)\n")
ns = {"__name__": "sim_v2_diag", "__file__": str(HERE / "vendor/commons/commons_v2/sim_v2.py")}
exec(compile(src2, "sim_v2_diag", "exec"), ns)
A = []
for seed in range(20):
    ns["DIAG"]["grace"] = 0; ns["DIAG"]["max_run"] = 0
    res = ns["run"]("V2_FULL", seed)
    A.append(dict(seed=seed, equals_october=(res == stored[seed]), grace_events=ns["DIAG"]["grace"], longest_stay=ns["DIAG"]["max_run"]))
# v1 for comparison: does v1's grace fire? (v1 FULL, 600 steps, seeds 0..4, counting line added the same way)
v1src = (HERE / "vendor/commons/commons_sim/sim.py").read_text()
# ---- B
S.STEPS = 20000
B = []
for seed in (0, 1):
    orig = S.run("V2_FULL", seed)
    mine, _ = CC.run("V2_FULL", seed, 20000)
    B.append(dict(seed=seed, ticks=20000, equal=(orig == mine), october_function=orig, century_runner=mine))
S.STEPS = 600
out = dict(A_grace_at_600=A, A_total_grace=sum(x["grace_events"] for x in A), A_longest_stay=max(x["longest_stay"] for x in A),
           A_all_equal_october=all(x["equals_october"] for x in A), B_past_600=B, B_all_equal=all(x["equal"] for x in B))
txt = json.dumps(out, indent=1, sort_keys=True)
(HERE / "diag/results_diag.json").write_text(txt)
print(json.dumps({k: v for k, v in out.items() if k not in ("A_grace_at_600", "B_past_600")}))
print([ (x["seed"], x["grace_events"], x["longest_stay"]) for x in A])
print([(x["seed"], x["equal"], x["october_function"]["pop_final"], x["century_runner"]["pop_final"]) for x in B])
print("receipt", hashlib.sha256(txt.encode()).hexdigest())
