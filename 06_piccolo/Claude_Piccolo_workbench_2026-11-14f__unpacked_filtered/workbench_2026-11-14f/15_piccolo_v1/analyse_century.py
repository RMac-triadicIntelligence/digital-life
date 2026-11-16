"""Piccolo v1: measures M1 to M12 (PREREG section 2) from the century outputs. Reads only; writes results_century.json."""
import hashlib
import itertools
import json
import math
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUALIFY = 30          # PREREG: members with at least 30 relevant deposits
SAME_COLOUR = 0.05    # PREREG: L1 distance below which two colours count as the same
OVERLAP = 0.5         # PREREG: place overlap line


def colour(c, t, f):
    n = c + t + f
    return (c / n, t / n, f / n)


def entropy(p):
    return -sum(x * math.log(x) for x in p if x > 0)


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def place_hist(m):
    h = {}
    for f in ("cur", "tel", "tru"):
        for cell, count, _first, _last in m["places"][f]:
            h[cell] = h.get(cell, 0) + count
    n = sum(h.values())
    return {k: v / n for k, v in h.items()} if n else {}


def overlap(p, q):
    return sum(min(v, q.get(k, 0.0)) for k, v in p.items())


def one(path):
    raw = path.read_bytes(); d = json.loads(raw)
    tpd = d["ticks_per_day"]; tot = d["totals"]; alive = d["members_alive"]
    cols = d["members_dead_columns"]; dead = [dict(zip(cols, r)) for r in d["members_dead"]]
    everyone = [dict(id=m["id"], cur=m["cur"], tel=m["tel"], tru=m["tru"], grace=m["grace"], born=m["born"], died=m["died"]) for m in alive] + \
               [dict(id=m["id"], cur=m["cur"], tel=m["tel"], tru=m["tru"], grace=m["grace"], born=m["born"], died=m["died"]) for m in dead]
    qual = [m for m in everyone if m["cur"] + m["tel"] + m["tru"] >= QUALIFY]
    for m in qual:
        m["colour"] = colour(m["cur"], m["tel"], m["tru"]); m["scout"] = (m["id"] % 3 == 0)
    scouts = [m for m in qual if m["scout"]]; keepers = [m for m in qual if not m["scout"]]
    names = ("curiosity", "verbosity", "formality")

    def med(group):
        return [round(st.median(m["colour"][i] for m in group), 4) for i in range(3)] if group else None

    def rarest(group):
        md = med(group); return names[md.index(min(md))] if md else None

    commonest_formality = sum(1 for m in qual if m["colour"][2] == max(m["colour"])) / len(qual) if qual else None
    # living qualifying members
    lq = [m for m in alive if m["cur"] + m["tel"] + m["tru"] >= QUALIFY]
    for m in lq:
        m["colour"] = colour(m["cur"], m["tel"], m["tru"]); m["ph"] = place_hist(m)
    by_house = {}
    for m in lq:
        by_house.setdefault(m["household"], []).append(m)
    within = [l1(a["colour"], b["colour"]) for ms in by_house.values() for a, b in itertools.combinations(ms, 2)]
    houses = [ms for ms in by_house.values() if len(ms) >= 2]
    fuller = 0
    for ms in houses:
        pooled = colour(sum(m["cur"] for m in ms), sum(m["tel"] for m in ms), sum(m["tru"] for m in ms))
        fuller += entropy(pooled) > max(entropy(m["colour"]) for m in ms)
    same = [(a, b) for a, b in itertools.combinations(lq, 2) if l1(a["colour"], b["colour"]) < SAME_COLOUR]
    ovs = [overlap(a["ph"], b["ph"]) for a, b in same]
    all_ovs = [overlap(a["ph"], b["ph"]) for a, b in itertools.combinations(lq, 2)]
    dw, de = tot["kin_dist_witnessed"], tot["kin_dist_expired"]
    grace_receivers = sum(1 for m in everyone if m["grace"] > 0)
    lifetimes = [(m["died"] - m["born"]) // tpd for m in dead if m["died"] is not None]
    summ = d["october_style_summary"]
    return dict(
        seed=d["seed"], output_sha256=hashlib.sha256(raw).hexdigest(), days=d["days"],
        M1_survived=bool(alive), extinct_at_day=(d["extinct_at_tick"] // tpd if d["extinct_at_tick"] is not None else None),
        M2_pop_final=len(alive), M2_pop_peak=summ["pop_peak"], M2_cap_hit=summ["cap_hit"],
        M3_lineages_alive=len({m["lineage"] for m in alive}),
        M4_oldest_born_day=(min(m["born"] for m in alive) // tpd if alive else None),
        M4_founders_alive=sum(1 for m in alive if m["id"] < 24),
        ever_born=len(everyone), deaths=tot["deaths"],
        median_lifetime_days_of_the_dead=(st.median(lifetimes) if lifetimes else None),
        M5_finds_laid=tot["finds_laid"], M5_finds_witnessed=tot["finds_witnessed"], M5_finds_expired=tot["finds_expired"],
        M5_share_expired=round(tot["finds_expired"] / tot["finds_laid"], 4) if tot["finds_laid"] else None,
        M6_kin_dist_witnessed=round(dw[0] / dw[1], 3) if dw[1] else None,
        M6_kin_dist_expired=round(de[0] / de[1], 3) if de[1] else None,
        M7_qualifying_members=len(qual), M7_scouts=len(scouts), M7_keepers=len(keepers),
        M7_scout_mean_curiosity=round(st.mean(m["colour"][0] for m in scouts), 4) if scouts else None,
        M7_keeper_mean_curiosity=round(st.mean(m["colour"][0] for m in keepers), 4) if keepers else None,
        M7_median_colour_scout=med(scouts), M7_median_colour_keeper=med(keepers),
        M7_rarest_for_median_scout=rarest(scouts), M7_rarest_for_median_keeper=rarest(keepers),
        M7_share_with_formality_commonest=round(commonest_formality, 4) if commonest_formality is not None else None,
        M8_living_qualifying=len(lq), M8_mean_colour_distance_within_household=round(st.mean(within), 4) if within else None,
        M9_households_compared=len(houses), M9_households_fuller_than_most_even_member=fuller,
        M10_same_colour_pairs=len(same),
        M10_share_in_different_places=round(sum(1 for o in ovs if o < OVERLAP) / len(ovs), 4) if ovs else None,
        M10_mean_place_overlap_same_colour=round(st.mean(ovs), 4) if ovs else None,
        M10_mean_place_overlap_all_pairs=round(st.mean(all_ovs), 4) if all_ovs else None,
        M11_ranging_unknown=tot["ranging_unknown"],
        M11_share_found=round(tot["ranging_unknown_found"] / tot["ranging_unknown"], 4) if tot["ranging_unknown"] else None,
        M12_grace_events=tot["grace"], M12_grace_receivers=grace_receivers,
        # --- supplementary, ADDED AFTER the first four seeds were seen (not in the prereg) ---
        S_living_scouts=sum(1 for m in alive if m["id"] % 3 == 0), S_living_keepers=sum(1 for m in alive if m["id"] % 3 != 0),
        S_scouts_ever=sum(1 for m in everyone if m["id"] % 3 == 0), S_keepers_ever=sum(1 for m in everyone if m["id"] % 3 != 0),
        S_scouts_dead=sum(1 for m in dead if m["id"] % 3 == 0), S_keepers_dead=sum(1 for m in dead if m["id"] % 3 != 0),
        S_last_keeper_death_day=max((m["died"] // tpd for m in dead if m["id"] % 3 != 0), default=None),
        S_last_death_day=max((m["died"] // tpd for m in dead), default=None),
        S_births_by_year={str(y["year"]): y["births"] for y in d["yearly"] if y["year"] in (1, 2, 5, 20, 50, 100)},
        S_deaths_by_year={str(y["year"]): y["deaths"] for y in d["yearly"] if y["year"] in (1, 2, 5, 20, 50, 100)},
        S_energy_final_min_median_max=([round(min(m["e"] for m in alive), 1), round(st.median(m["e"] for m in alive), 1),
                                        round(max(m["e"] for m in alive), 1)] if alive else None),
        S_stock_min_over_century=summ["stock_min"], S_stuck_frac=summ["stuck_frac"],
        pop_by_decade=[y["pop"] for y in d["yearly"] if y["year"] % 10 == 0],
        stock_by_decade=[y["stock"] for y in d["yearly"] if y["year"] % 10 == 0],
        lineages_by_decade=[y["lineages"] for y in d["yearly"] if y["year"] % 10 == 0],
        e_mean_by_decade=[y["e_mean"] for y in d["yearly"] if y["year"] % 10 == 0],
    )


if __name__ == "__main__":
    folder = HERE / (sys.argv[1] if len(sys.argv) > 1 else "century")
    rows = [one(p) for p in sorted(folder.glob("seed_*.json"))]
    txt = json.dumps({"seeds_reported": [r["seed"] for r in rows], "per_seed": rows}, indent=1, sort_keys=True)
    (HERE / (sys.argv[2] if len(sys.argv) > 2 else "results_century.json")).write_text(txt)
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if not k.endswith("by_decade")}, sort_keys=True))
    print("receipt", hashlib.sha256(txt.encode()).hexdigest())
