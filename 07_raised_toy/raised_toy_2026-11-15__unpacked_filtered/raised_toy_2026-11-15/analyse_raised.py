"""RAISED toy: one table per arm. Written and frozen before any toy run.

Usage: python3 analyse_raised.py <ticks> <label=dir> [<label=dir> ...]  > summary.json
Each dir holds seed_XX.json (the packed output), seed_XX.json.diag.json and, for toy arms, seed_XX.json.arm.json.
"""
import json, sys, glob, statistics as st
from pathlib import Path

T = int(sys.argv[1])
YEAR = 8 * 365
AGES = (80, 240, 800)   # 10 days, 30 days, 100 days


def med(v): return round(st.median(v), 2) if v else None


def one(dirpath):
    seeds = {}
    pool = {"KN": [], "SN": [], "KF": [], "SF": []}
    for f in sorted(glob.glob(str(Path(dirpath) / "seed_??.json"))):
        d = json.load(open(f)); seed = d["seed"]
        dg = json.load(open(f + ".diag.json"))
        armf = Path(f + ".arm.json")
        arm = json.load(open(armf)) if armf.exists() else {}
        y = d["yearly"]; alive = d["members_alive"]
        lin_roles = {}
        for m in alive:
            lin_roles.setdefault(m["lineage"], set()).add("S" if m["scout"] else "K")
        r = dict(
            pop=len(alive), keepers_alive=sum(1 for m in alive if not m["scout"]),
            scouts_alive=sum(1 for m in alive if m["scout"]),
            lineages_alive=len(lin_roles), lineages_with_both=sum(1 for v in lin_roles.values() if len(v) == 2),
            households=len({m["household"] for m in alive}),
            births_total=y[-1]["births"] if y else None,
            births_after_y1=(y[-1]["births"] - y[0]["births"]) if y else None,
            deaths_after_y1=(y[-1]["deaths"] - y[0]["deaths"]) if y else None,
            stock_yearly_mean=round(sum(v["stock"] for v in y) / len(y), 3) if y else None,
            stock_last=y[-1]["stock"] if y else None,
            e_max_final=max((m["e"] for m in alive), default=None),
            cap_hit=d["october_style_summary"]["cap_hit"], extinct_at=d["extinct_at_tick"],
            pop_by_year=[v["pop"] for v in y],
            s_given=round(arm.get("s_given", 0.0), 2), s_gifts=arm.get("s_gifts", 0),
            f_given=round(arm.get("f_given", 0.0), 2), f_gifts=arm.get("f_gifts", 0),
            returned=round(arm.get("returned", 0.0), 2), max_after_cap=arm.get("max_after_cap"),
            with_ticks=arm.get("with_ticks", 0), with_no_keeper=arm.get("with_no_keeper", 0))
        # keepers alive at the end of each year, from birth and death ticks
        r["keepers_by_year"] = [sum(1 for m in dg if not m["scout"] and m["born"] < (k + 1) * YEAR and (m["died"] is None or m["died"] >= (k + 1) * YEAR))
                                for k in range(T // YEAR)]
        for m in dg:
            g = ("S" if m["scout"] else "K") + ("F" if m["parent"] is None else "N")
            pool[g].append(m)
        seeds[seed] = r
    pooled = {}
    for g, ms in pool.items():
        dead = [m for m in ms if m["died"] is not None]
        p = dict(n=len(ms), dead=len(dead), alive=len(ms) - len(dead),
                 life_median_of_dead=med([m["died"] - m["born"] for m in dead]),
                 life_max_of_dead=max((m["died"] - m["born"] for m in dead), default=None),
                 intake_per_tick=round(sum(m["intake"] for m in ms) / max(sum(m["ticks"] for m in ms), 1), 5),
                 got_s=round(sum(m.get("got_s", 0.0) for m in ms), 2), got_f=round(sum(m.get("got_f", 0.0) for m in ms), 2),
                 gave_s=round(sum(m.get("gave_s", 0.0) for m in ms), 2), gave_f=round(sum(m.get("gave_f", 0.0) for m in ms), 2),
                 returned=round(sum(m.get("returned", 0.0) for m in ms), 2), survive={})
        for age in AGES:
            elig = [m for m in ms if m["born"] + age <= T]
            ok = [m for m in elig if m["died"] is None or m["died"] - m["born"] >= age]
            p["survive"][str(age)] = [len(ok), len(elig), round(len(ok) / len(elig), 4) if elig else None]
        mt = {}
        for m in ms:
            for k, v in m["mode_ticks"].items(): mt[k] = mt.get(k, 0) + v
        tot = sum(mt.values())
        p["mode_share"] = {k: round(v / tot, 4) for k, v in sorted(mt.items())} if tot else {}
        pooled[g] = p
    return dict(seeds=seeds, pooled=pooled)


out = {"ticks": T, "arms": {}}
for spec in sys.argv[2:]:
    label, d = spec.split("=", 1)
    out["arms"][label] = one(d)
print(json.dumps(out, indent=1, sort_keys=True))
