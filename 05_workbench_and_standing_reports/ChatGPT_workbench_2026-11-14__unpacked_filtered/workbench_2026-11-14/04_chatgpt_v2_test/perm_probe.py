"""Conductor probe. Uses ChatGPT's own dwelling.UncertaintyBasin, choice.Choice, character.Shape and protocol,
unchanged, with NO body, NO world, NO tape, NO kernel. If this reproduces every final character in the evidence,
character formation in v2 does not depend on anything the member lived through in the Commons."""
import sys, json, itertools, random, statistics
from collections import Counter, defaultdict
sys.path.insert(0, '.')
import numpy as np
from dwelling import UncertaintyBasin
from choice import Choice
from character import Shape, CURIOSITY_STEP, FORMALITY_STEP
import protocol as P

def form(history, start=(0.6, 0.5), freeze=False):
    basin = UncertaintyBasin(); choice = Choice("ACTIVE")
    ch = {"curiosity": start[0], "formality": start[1], "verbosity": 0.5}
    seam_open = False; signed = 0; questions = 0; log = []
    for tick in range(P.TICKS):
        basin.step(tick, history.get(tick))
        shape = Shape(**ch)
        views = basin.views(tick)
        if tick in (9, 13, 20) and not seam_open:
            d = choice.surface(shape, views)
            if d["selected"] != "keep_open":
                basin.surface(d["selected"]); questions += 1
        if tick not in (*P.SIGNING_TICKS, P.LATE_REVIEW) or seam_open:
            continue
        d = choice.review(shape, views)
        cat = d["selected"]
        if cat == "hold_open":
            continue
        view = next(v for v in views if v["category"] == cat)
        step = CURIOSITY_STEP if cat == "curiosity" else FORMALITY_STEP
        direction = 1 if view["leader"] == "favor_first" else -1
        target = round(min(0.96, max(0.04, ch[cat] + direction * step)), 3)
        if ch[cat] == target:
            continue
        delta = target - ch[cat]
        if tick >= P.SILENCE_START or freeze or tick not in P.SIGNING_TICKS or not 0 < abs(delta) <= 0.080001:
            if not (freeze and tick < P.SILENCE_START):
                seam_open = True
            continue
        ch[cat] = target; signed += 1; log.append((tick, cat, direction)); basin.surface(cat)
    return (ch["curiosity"], ch["formality"]), signed, questions, tuple(log)

def base_reads(seed):
    cal = np.random.default_rng(np.random.SeedSequence([seed, 308]))
    offsets = cal.integers(-3, 4, size=len(P.STRUCTURED)).tolist()
    return [P.make_read(i, code, offsets[i]) for i, code in enumerate(P.STRUCTURED)]

def with_late(reads):
    h = dict(zip(P.REARING_TICKS, reads, strict=True))
    for tick, code in ((18, "source"), (19, "witness"), (20, "source"), (21, "witness")):
        h[tick] = P.make_read(tick, code)
    return h

if __name__ == "__main__":
    # 1. validation against the packaged evidence and the conductor's fresh seeds
    ok = bad = 0
    for folder in sys.argv[1:]:
        S = json.load(open(f"{folder}/summary.json"))
        for r in S:
            arm = r["arm"]
            hist = {"LISTEN": "LISTEN", "REVERSE": "REVERSE", "SHUFFLED": "SHUFFLED", "RANDOM": "RANDOM",
                    "ALT_SEED_LISTEN": "LISTEN", "CHARACTER_FROZEN_LISTEN": "LISTEN"}.get(arm, "VERIFY")
            if arm.startswith("LATENCY") or arm.endswith("_BODY") or arm.endswith("_FROZEN"):
                continue
            start = (r["initial_character"]["curiosity"], r["initial_character"]["formality"])
            final, signed, q, _ = form(P.social_reads(r["seed"], hist), start, freeze=arm.startswith("CHARACTER_FROZEN"))
            want = (r["final_character"]["curiosity"], r["final_character"]["formality"])
            good = final == want and signed == r.get("signed_changes", 0) and q == r.get("questions", 0)
            ok += good; bad += not good
    print(f"VALIDATION: tape-free harness reproduced final character, signed-change count and question count for {ok} readers; mismatches {bad}")
    # 2. permutations of the same 12 encounters
    rng = random.Random(20261114)
    N = 4000
    agg = Counter(); per_seed = []
    for seed in list(range(204, 212)) + list(range(7001, 7009)):
        reads = base_reads(seed)
        fwd = form(with_late(reads))[0]; rev = form(with_late(reads[::-1]))[0]
        outcomes = Counter()
        for _ in range(N):
            p = reads[:]; rng.shuffle(p)
            outcomes[form(with_late(p))[0]] += 1
        same = outcomes[fwd] / N
        per_seed.append((seed, fwd, rev == fwd, round(same, 3), len(outcomes)))
        agg.update(outcomes)
    for row in per_seed: print("seed %d forward %s reverse_equal %s share_of_random_orders_equal_to_forward %.3f distinct_outcomes %d" % row)
    print("mean share of random orders that end where forward order ends:", round(statistics.mean(r[3] for r in per_seed), 3))
    tot = sum(agg.values())
    print("outcomes over all sampled orders:", [(k, round(v / tot, 3)) for k, v in agg.most_common(12)])
