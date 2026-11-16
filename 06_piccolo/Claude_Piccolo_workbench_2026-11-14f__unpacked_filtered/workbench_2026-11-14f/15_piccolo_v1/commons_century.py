"""Piccolo v1, Part 1: the 13 Oct commons (commons_v2) run for a parameterised length, with read-only deposits.

PREREG.md (frozen first) says what this is. Rules of the swarm are October's, copied from sim_v2.run.
Differences from sim_v2.run, all claimed to change nothing a living member does:
  1. the length T is a parameter (October fixed it at 600);
  2. dead members are dropped from the working list (order of the living unchanged);
  3. households with no living member are dropped;
  4. a recorder lays down deposits. It draws no random numbers and writes to nothing the swarm reads.
check_600.py proves 1 to 4 against October's stored results before any century is run.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor" / "commons" / "commons_v2"))
import sim_v2 as S  # noqa: E402  October's swarm, unedited; it checks its own prereg hash on import

SIM_V2_SHA = "b5cbf3b5b6194a7f2930645e7c02742009abf8f7c1de2926248bd98af5ca2e73"
assert hashlib.sha256((HERE / "vendor/commons/commons_v2/sim_v2.py").read_bytes()).hexdigest() == SIM_V2_SHA

v1 = S.v1
N, SEASON, NPATCH = S.N, S.SEASON, S.NPATCH
REGROW, SEED_FOOD, KFLOOR = S.REGROW, S.SEED_FOOD, S.KFLOOR
NOISE, EAT, METAB, E0 = S.NOISE, S.EAT, S.METAB, S.E0
FAMS, FOUNDERS, WITNESS_T, WITNESS_TOL = S.FAMS, S.FOUNDERS, S.WITNESS_T, S.WITNESS_TOL
D_TOL, D_UP, D_DOWN, D_STAY, RADIUS = S.D_TOL, S.D_UP, S.D_DOWN, S.D_STAY, S.RADIUS
GRACE_EVERY, GRACE_MIN, JUBILEE = S.GRACE_EVERY, S.GRACE_MIN, S.JUBILEE
BIRTH_EVERY, BIRTH_HARVEST, BIRTH_STOCK, BIRTH_COST, SPLIT_E, SAFETY_CAP = (
    S.BIRTH_EVERY, S.BIRTH_HARVEST, S.BIRTH_STOCK, S.BIRTH_COST, S.SPLIT_E, S.SAFETY_CAP)
SPACING_W, WEAN_W, WEAN_TAU, WEAN_FLOOR = S.SPACING_W, S.WEAN_W, S.WEAN_TAU, S.WEAN_FLOOR
DWELL_FOOD, SCOUT_EVERY, CALL_LOW, CALL_VALUE, BUD_SIZE = (
    S.DWELL_FOOD, S.SCOUT_EVERY, S.CALL_LOW, S.CALL_VALUE, S.BUD_SIZE)
Agent, Family, step_toward, window = S.Agent, S.Family, S.step_toward, S.window

TICKS_PER_DAY = 8          # PREREG: one day = 8 swarm ticks
DAYS_PER_YEAR = 365
KNOWN = 0.2                # the swarm's own known-ground line (sim_v2: m = fam.C > 0.2)
FACES = ("cur", "tel", "tru")   # curiosity, verbosity ("tell"), formality ("trust")


class Member:
    """What the recorder holds about one member. Never read by the swarm."""
    __slots__ = ("id", "lineage", "born", "died", "obs", "cur", "tel", "tru", "nothing", "finds_laid",
                 "finds_wit", "finds_exp", "witnessed_others", "grace", "places", "first")

    def __init__(self, aid, lineage, born):
        self.id, self.lineage, self.born, self.died = aid, lineage, born, None
        self.obs = self.cur = self.tel = self.tru = self.nothing = 0
        self.finds_laid = self.finds_wit = self.finds_exp = self.witnessed_others = self.grace = 0
        self.places = {f: {} for f in FACES}      # cell -> [count, first_day, last_day]
        self.first = {f: None for f in FACES}     # (tick, x, y, observed value or call value)

    def lay(self, face, t, x, y, val):
        setattr(self, face, getattr(self, face) + 1)
        day = t // TICKS_PER_DAY
        cell = x * N + y
        rec = self.places[face].get(cell)
        if rec is None:
            self.places[face][cell] = [1, day, day]
        else:
            rec[0] += 1; rec[2] = day
        if self.first[face] is None:
            self.first[face] = [int(t), int(x), int(y), round(float(val), 6)]


class Recorder:
    def __init__(self):
        self.m = {}
        self.grid_exp = np.zeros((N, N), dtype=np.int64)
        self.grid_wit = np.zeros((N, N), dtype=np.int64)
        self.find_laid = self.find_wit = self.find_exp = 0
        self.dist = {}                         # pending tuple -> distance to nearest kin when laid (or None)
        self.dw_sum = self.dw_n = self.de_sum = self.de_n = 0
        self.births = self.deaths = self.grace = 0
        self.rang_unknown = self.rang_unknown_found = 0
        self.yearly = []


def _kin_dist(a, kin):
    best = None
    for b in kin:
        if b.id == a.id:
            continue
        dx = abs(a.x - b.x); dx = min(dx, N - dx)
        dy = abs(a.y - b.y); dy = min(dy, N - dy)
        d = dx if dx > dy else dy
        if best is None or d < best:
            best = d
    return best


def run(variant, seed, T, record=True, stop_when_extinct=False):
    """Body copied from sim_v2.run. Lines marked [rec] or [house] are the only additions.

    stop_when_extinct ends the loop once nobody is alive (century runs). It is off for the 600-step check,
    because October's loop kept turning the empty world and its stock minimum is taken over all 600 steps.
    """
    wrng = np.random.default_rng([seed, 1]); arng = np.random.default_rng([seed, 2])
    centres = [tuple(wrng.integers(0, N, 2)) for _ in range(NPATCH)]
    K = v1.capacity(centres); R = K.copy(); R0 = R.sum()
    lone = variant == "V2_LONE"
    spacing = variant != "NO_SPACING"; roles = variant != "NO_ROLES"
    budding = variant not in ("NO_BUDDING", "V2_SELF_REPLICATING", "V2_LONE")
    weaning = variant != "NO_WEANING"
    direct = variant in ("V2_NO_CONSTITUTION", "V2_LONE")
    fams, agents, nid, nfam = {}, [], 0, 0
    rec = Recorder() if record else None                                                   # [rec]
    for f in range(FAMS):
        if not lone:
            fams[nfam] = Family(); fid = nfam; nfam += 1
        for _ in range(FOUNDERS):
            if lone:
                fams[nfam] = Family(); fid = nfam; nfam += 1
            x, y = (int(v) for v in arng.integers(0, N, 2))
            agents.append(Agent(nid, fid, f, x, y, E0, np.zeros((N, N)), 0))
            if rec: rec.m[nid] = Member(nid, f, 0)                                         # [rec]
            nid += 1
    out = dict(h=0.0, late=0.0, post=0.0, smin=1.0, peak=0, me=0.0, men=0, ast=0, stuck=0, cap=False)
    extinct_at = None                                                                      # [rec]
    for t in range(T):
        if t > 0 and t % SEASON == 0:
            centres = [tuple(wrng.integers(0, N, 2)) for _ in range(NPATCH)]; K = v1.capacity(centres)
        live = [a for a in agents if a.alive]
        occ = {}
        for a in live:
            g = occ.setdefault(a.fam, np.zeros((N, N))); g[a.x, a.y] += 1
        crowd = {f: sum(np.roll(np.roll(g, dx, 0), dy, 1) for dx in (-1, 0, 1) for dy in (-1, 0, 1)) for f, g in occ.items()}
        if rec:                                                                            # [rec]
            byfam = {}
            for a in live:
                byfam.setdefault(a.fam, []).append(a)
        order = arng.permutation(len(live)); ht = 0.0
        for i in order:
            a = live[i]; fam = fams[a.fam]
            obs = R[a.x, a.y] + NOISE * arng.standard_normal()
            if abs(obs - a.belief[a.x, a.y]) > D_TOL:
                a.d += D_UP * (1 - a.d)
            else:
                a.d -= D_DOWN * a.d
            a.belief[a.x, a.y] = obs
            if rec:                                                                        # [rec] read before the family map is touched
                mm = rec.m[a.id]; mm.obs += 1
                c_here = fam.C[a.x, a.y]
                if c_here <= KNOWN:
                    if a.run == 0:
                        rec.rang_unknown += 1
                        if obs > CALL_VALUE:
                            rec.rang_unknown_found += 1
                            mm.lay("cur", t, a.x, a.y, obs)
                        else:
                            mm.nothing += 1
                elif abs(obs - fam.M[a.x, a.y]) < WITNESS_TOL:
                    mm.lay("tru", t, a.x, a.y, obs)
            if direct:
                fam.M[a.x, a.y], fam.C[a.x, a.y], fam.T[a.x, a.y] = obs, 1.0, t
            else:
                hit = None
                for k, (px, py, v, pid, pt) in enumerate(fam.pending):
                    if px == a.x and py == a.y and pid != a.id and t - pt <= WITNESS_T and abs(v - obs) < WITNESS_TOL:
                        hit = k; break
                if hit is not None:
                    ptuple = fam.pending[hit] if rec else None                             # [rec]
                    px, py, v, pid, pt = fam.pending.pop(hit)
                    fam.M[a.x, a.y], fam.C[a.x, a.y], fam.T[a.x, a.y] = (v + obs) / 2, 1.0, t
                    if rec:                                                                # [rec]
                        mm.witnessed_others += 1
                        caller = rec.m[pid]
                        caller.lay("tel", t, px, py, v)
                        if v > CALL_VALUE:
                            caller.finds_wit += 1; rec.find_wit += 1; rec.grid_wit[px, py] += 1
                            d = rec.dist.pop(ptuple, None)
                            if d is not None:
                                rec.dw_sum += d; rec.dw_n += 1
                else:
                    fam.pending.append((a.x, a.y, obs, a.id, t))
                    if rec and obs > CALL_VALUE:                                           # [rec]
                        mm.finds_laid += 1; rec.find_laid += 1
                        rec.dist[(a.x, a.y, obs, a.id, t)] = _kin_dist(a, byfam[a.fam])
            e = min(EAT, R[a.x, a.y]); R[a.x, a.y] -= e
            a.e += e - METAB; ht += e; fam.period_harvest += e
        # love: sharing never stops; copying fades with experience (weaning)
        for a in live:
            fam = fams[a.fam]
            w = WEAN_W * max(WEAN_FLOOR / WEAN_W, np.exp(-(t - a.born) / WEAN_TAU)) if weaning else WEAN_W
            a.belief += w * fam.C * (fam.M - a.belief)
        # move: dwell where it matters, scouts explore, keepers spread out, calls for witness
        for a in live:
            out["ast"] += 1; fam = fams[a.fam]
            if a.target is not None:
                if (a.x, a.y) == a.target:
                    a.target = None
                else:
                    step_toward(a, *a.target); continue
            here = a.belief[a.x, a.y]
            if a.d > D_STAY and here > DWELL_FOOD:
                a.run += 1; out["stuck"] += 1; continue
            a.run = 0
            xs, ys = window(a)
            scout = roles and a.id % SCOUT_EVERY == 0
            if scout:
                sub = fam.C[np.ix_(xs, ys)] + 1e-3 * arng.random((2 * RADIUS + 1, 2 * RADIUS + 1))
                i, j = np.unravel_index(int(np.argmin(sub)), sub.shape)
            else:
                sub = a.belief[np.ix_(xs, ys)]
                if spacing and a.fam in crowd:
                    c = crowd[a.fam][np.ix_(xs, ys)].copy(); c[RADIUS, RADIUS] -= 1  # not counting itself
                    sub = sub - SPACING_W * c
                if a.belief[np.ix_(xs, ys)].max() <= CALL_LOW and not direct:
                    calls = [p for p in fam.pending if p[2] > CALL_VALUE and p[3] != a.id]
                    if calls:
                        p = max(calls, key=lambda q: q[4]); a.target = (p[0], p[1]); step_toward(a, p[0], p[1]); continue
                if a.belief[np.ix_(xs, ys)].max() <= 0.05:
                    a.x = (a.x + int(arng.integers(-1, 2))) % N; a.y = (a.y + int(arng.integers(-1, 2))) % N; continue
                i, j = np.unravel_index(int(np.argmax(sub)), sub.shape)
            a.x = (a.x + int(np.sign(i - RADIUS))) % N; a.y = (a.y + int(np.sign(j - RADIUS))) % N
        # grace toward the frontier: kin's most recent confirmed discovery
        if t % GRACE_EVERY == 0:
            cand = [a for a in live if a.run >= GRACE_MIN]
            if cand:
                a = max(cand, key=lambda z: (z.run, -z.id)); fam = fams[a.fam]
                a.d, a.run = 0.3, 0
                fresh = np.where(fam.M > CALL_VALUE, fam.T, -1)
                if fresh.max() >= 0:
                    a.target = tuple(int(v) for v in np.unravel_index(int(np.argmax(fresh)), fresh.shape))
                if rec: rec.m[a.id].grace += 1; rec.grace += 1                             # [rec]
        for fam in fams.values():
            fam.C *= JUBILEE
            if rec:                                                                        # [rec] count what is about to expire
                for p in fam.pending:
                    if t - p[4] > WITNESS_T and p[2] > CALL_VALUE:
                        rec.find_exp += 1; rec.grid_exp[p[0], p[1]] += 1
                        mm = rec.m.get(p[3])
                        if mm is not None: mm.finds_exp += 1
                        d = rec.dist.pop(p, None)
                        if d is not None:
                            rec.de_sum += d; rec.de_n += 1
            fam.pending = [p for p in fam.pending if t - p[4] <= WITNESS_T]
        for a in live:
            if a.e <= 0:
                a.alive = False
                if rec: rec.m[a.id].died = t; rec.deaths += 1                              # [rec]
        agents = [a for a in agents if a.alive]                                            # [house] drop the dead
        live = [a for a in agents if a.alive]
        # births
        if variant == "V2_SELF_REPLICATING":
            for a in list(live):
                if a.e > SPLIT_E:
                    if len(live) >= SAFETY_CAP:
                        out["cap"] = True; continue
                    a.e /= 2
                    agents.append(Agent(nid, a.fam, a.lineage, a.x, a.y, a.e, fams[a.fam].M.copy(), t))
                    if rec: rec.m[nid] = Member(nid, a.lineage, t); rec.births += 1        # [rec]
                    nid += 1
                    live.append(agents[-1])
        elif t > 0 and t % BIRTH_EVERY == 0:
            if budding:
                for fid in list(fams):
                    members = sorted([a for a in live if a.fam == fid], key=lambda z: z.id)
                    if len(members) > BUD_SIZE:
                        old = fams[fid]; nf = nfam; nfam += 1
                        fams[nf] = Family(old.M, old.C, old.T)
                        for a in members[len(members) // 2:]:
                            a.fam = nf
            if R.sum() >= BIRTH_STOCK * R0:
                for fid, fam in list(fams.items()):
                    members = [a for a in live if a.fam == fid]
                    if members and fam.period_harvest > BIRTH_HARVEST and len(live) < SAFETY_CAP:
                        p = max(members, key=lambda z: (z.e, -z.id))
                        if p.e > BIRTH_COST:
                            p.e -= BIRTH_COST
                            if lone:
                                nf = nfam; nfam += 1; fams[nf] = Family(); belief = np.zeros((N, N))
                            else:
                                nf = fid; belief = fam.M.copy()
                            agents.append(Agent(nid, nf, p.lineage, p.x, p.y, BIRTH_COST, belief, t))
                            if rec: rec.m[nid] = Member(nid, p.lineage, t); rec.births += 1  # [rec]
                            nid += 1
                            live.append(agents[-1])
            for fam in fams.values():
                fam.period_harvest = 0.0
        Keff = np.maximum(K, KFLOOR)
        R = np.clip(R + REGROW * R * (1 - R / Keff) + SEED_FOOD, 0, None)
        out["h"] += ht
        if t >= 300:
            out["late"] += ht
        if any(s <= t < s + 50 for s in (150, 300, 450)):
            out["post"] += ht
        out["smin"] = min(out["smin"], R.sum() / R0); out["peak"] = max(out["peak"], len(live))
        for fid, fam in fams.items():
            m = fam.C > 0.2
            if m.any() and any(a.fam == fid for a in live):
                out["me"] += float(np.abs(fam.M[m] - R[m]).mean()); out["men"] += 1
        occupied = {a.fam for a in live}                                                   # [house] drop empty households
        if len(occupied) != len(fams):
            for fid in [f for f in fams if f not in occupied]:
                if rec:
                    for p in fams[fid].pending: rec.dist.pop(p, None)
                del fams[fid]
        if rec and (t + 1) % (TICKS_PER_DAY * DAYS_PER_YEAR) == 0:                          # [rec] yearly snapshot
            rec.yearly.append(dict(
                year=(t + 1) // (TICKS_PER_DAY * DAYS_PER_YEAR), pop=len(live),
                households=len({a.fam for a in live}), lineages=len({a.lineage for a in live}),
                stock=round(float(R.sum() / R0), 4), births=rec.births, deaths=rec.deaths, grace=rec.grace,
                finds_laid=rec.find_laid, finds_wit=rec.find_wit, finds_exp=rec.find_exp,
                oldest_born_day=(min(a.born for a in live) // TICKS_PER_DAY) if live else None,
                e_mean=round(float(np.mean([a.e for a in live])), 4) if live else None,
                e_max=round(float(max(a.e for a in live)), 4) if live else None))
        if not live and extinct_at is None:                                                # [rec] note the day the last member died
            extinct_at = t
            if stop_when_extinct:
                break
    live = [a for a in agents if a.alive]
    res = dict(harvest_total=round(float(out["h"]), 4), harvest_late=round(float(out["late"]), 4),
               post_shift=round(float(out["post"]), 4), stock_min=round(float(out["smin"]), 4),
               pop_final=len(live), pop_peak=out["peak"], families_alive=len({a.lineage for a in live}),
               households_final=len({a.fam for a in live}),
               map_error=round(out["me"] / max(out["men"], 1), 4), stuck_frac=round(out["stuck"] / max(out["ast"], 1), 4),
               per_capita=round(float(out["h"]) / max(out["ast"], 1), 5), cap_hit=out["cap"])
    if not rec:
        return res
    return res, pack(rec, live, T, extinct_at, variant, seed)


def _places(mm):
    return {f: [[int(c), int(v[0]), int(v[1]), int(v[2])] for c, v in sorted(mm.places[f].items())] for f in FACES}


def pack(rec, live, T, extinct_at, variant, seed):
    alive_ids = {a.id: a for a in live}
    members_alive, members_dead = [], []
    for aid in sorted(rec.m):
        mm = rec.m[aid]
        row = dict(id=mm.id, lineage=mm.lineage, born=mm.born, died=mm.died, scout=(mm.id % SCOUT_EVERY == 0),
                   obs=mm.obs, cur=mm.cur, tel=mm.tel, tru=mm.tru, nothing=mm.nothing,
                   finds_laid=mm.finds_laid, finds_wit=mm.finds_wit, finds_exp=mm.finds_exp,
                   witnessed_others=mm.witnessed_others, grace=mm.grace, first=mm.first)
        if aid in alive_ids:
            a = alive_ids[aid]
            row.update(household=int(a.fam), x=int(a.x), y=int(a.y), e=round(float(a.e), 4), places=_places(mm))
            members_alive.append(row)
        else:
            members_dead.append([mm.id, mm.lineage, mm.born, mm.died, mm.obs, mm.cur, mm.tel, mm.tru, mm.nothing,
                                 mm.finds_laid, mm.finds_wit, mm.finds_exp, mm.witnessed_others, mm.grace])
    return dict(
        build="piccolo_v1/commons_century", variant=variant, seed=seed, ticks=T, ticks_per_day=TICKS_PER_DAY,
        days=T // TICKS_PER_DAY, extinct_at_tick=extinct_at, sim_v2_sha256=SIM_V2_SHA,
        totals=dict(births=rec.births, deaths=rec.deaths, grace=rec.grace, finds_laid=rec.find_laid,
                    finds_witnessed=rec.find_wit, finds_expired=rec.find_exp,
                    kin_dist_witnessed=[rec.dw_sum, rec.dw_n], kin_dist_expired=[rec.de_sum, rec.de_n],
                    ranging_unknown=rec.rang_unknown, ranging_unknown_found=rec.rang_unknown_found),
        yearly=rec.yearly,
        grid_finds_expired=rec.grid_exp.tolist(), grid_finds_witnessed=rec.grid_wit.tolist(),
        members_alive=members_alive,
        members_dead_columns=["id", "lineage", "born", "died", "obs", "cur", "tel", "tru", "nothing", "finds_laid",
                              "finds_wit", "finds_exp", "witnessed_others", "grace"],
        members_dead=members_dead)


def dumps(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    seed = int(sys.argv[1]); T = int(sys.argv[2]); outp = Path(sys.argv[3])
    res, packed = run("V2_FULL", seed, T, stop_when_extinct=True)
    packed["october_style_summary"] = res
    txt = dumps(packed)
    outp.write_text(txt)
    print(seed, T, hashlib.sha256(txt.encode()).hexdigest(), res["pop_final"], flush=True)
