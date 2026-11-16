"""Conductor probes on ChatGPT v2 character formation, using the validated tape-free harness (perm_probe.form)."""
import sys, random, statistics
from collections import Counter
sys.path.insert(0, '.'); sys.path.insert(0, '/home/claude/cg2/report')
import numpy as np
import protocol as P
from perm_probe import form, base_reads, with_late
seeds = list(range(204, 212)) + list(range(7001, 7033))
def l1(a, b=(0.6, 0.5)): return round(abs(a[0]-b[0]) + abs(a[1]-b[1]), 6)

# A. noise at scale: category-matched random codes, same rule as his RANDOM arm, 200 draws per seed
rng = np.random.default_rng(20261114)
pools = {c: tuple(k for k, (t, _) in P.HISTORY_CODES.items() if t == c) for c in P.CATEGORIES}
cal = {s: np.random.default_rng(np.random.SeedSequence([s, 308])).integers(-3, 4, size=12).tolist() for s in seeds}
st = {"structured": [], "random": []}
for s in seeds:
    f, n, q, _ = form(with_late(base_reads(s))); st["structured"].append((n, l1(f), q))
    for _ in range(200):
        codes = [str(rng.choice(pools[P.HISTORY_CODES[c][0]])) for c in P.STRUCTURED]
        f, n, q, _ = form(with_late([P.make_read(i, c, cal[s][i]) for i, c in enumerate(codes)]))
        st["random"].append((n, l1(f), q))
for k, v in st.items():
    print(f"{k:10s} n={len(v):5d} signed changes per member {statistics.mean(x[0] for x in v):.2f}  moved at all {sum(x[1]>0 for x in v)/len(v):.1%}  mean net drift {statistics.mean(x[1] for x in v):.3f}  asked a question {sum(x[2]>0 for x in v)/len(v):.1%}")
print("random: share with at least as many signed changes as that seed's structured history:",
      round(sum(1 for i, s in enumerate(seeds) for x in st["random"][i*200:(i+1)*200] if x[0] >= st["structured"][i][0]) / len(st["random"]), 3))

# B. does the owner's review calendar set the character? Same forward history, different signing ticks.
orig = P.SIGNING_TICKS
out = {}
for sched in [(7, 11, 15), (6, 10, 14), (8, 12, 15), (5, 9, 13), (9, 12, 15), (7, 15), (11,), (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)]:
    P.SIGNING_TICKS = sched
    out[sched] = Counter(form(with_late(base_reads(s)))[0] for s in seeds)
P.SIGNING_TICKS = orig
for sched, c in out.items(): print("owner reviews at", sched, "-> final characters over 40 seeds:", c.most_common(4))
