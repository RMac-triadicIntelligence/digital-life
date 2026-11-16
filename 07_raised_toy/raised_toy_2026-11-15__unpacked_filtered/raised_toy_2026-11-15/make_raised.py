"""RAISED toy, 15 Nov 2026. Makes commons_raised.py from diag_keepers/commons_diag.py by asserted text swaps.

The 13 Oct commons is the baseline and is not edited. This file adds four switches, all OFF by default:
  H  a hand has a size: what a member holds above HAND at the end of the eating step goes back on the ground
  S  the sent feed the keepers: a scout's overflow goes first to keepers of its household who have room
  F  keepers feed the lambs: an adult keeper gives to a young member of its household beside it that is low
  W  with, then sent: a young member stays beside an adult keeper of its household for its first season
With every switch off the packed output must hash to the value on record for the unchanged runner.
Usage of the product:  python3 commons_raised.py <seed> <ticks> <out.json> <switches, e.g. HSFW or - >
"""
from pathlib import Path

SRC = Path("/home/claude/diag_keepers/commons_diag.py")
OUT = Path(__file__).resolve().parent / "commons_raised.py"
src = SRC.read_text()


def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:70])
    src = src.replace(old, new)


swap('MODES = "NTCDSBR"', 'MODES = "NTCDSBRW"')

ARM_CODE = '''
# ---------------- RAISED toy: switches and helpers (all read October's own constants) ----------------
ARM = {"H": False, "S": False, "F": False, "W": False}
HAND = E0                 # a hand is what a founder is born holding (1.0)            [candidate, hole T1]
YOUNG_TICKS = WEAN_TAU    # a member is young for October's own weaning time (100)    [candidate, hole T2]
LOW = BIRTH_COST          # a young member is low under the birth portion (0.5)       [candidate, hole T3]
AR = {}


def _ar_reset():
    AR.clear()
    AR.update(s_gifts=0, s_given=0.0, f_gifts=0, f_given=0.0, returned=0.0, returned_n=0, max_after_cap=0.0,
              with_ticks=0, with_no_keeper=0)


def _is_scout(a): return a.id % SCOUT_EVERY == 0
def _young(a, t): return a.born > 0 and (t - a.born) < YOUNG_TICKS
def _note(aid, key, v):
    d = DG.m.get(aid)
    if d is not None: d[key] = d.get(key, 0.0) + v


def _arm_after_eat(live, fams, R, t):
    """Runs once a tick, after every member has looked and eaten. Draws no random numbers."""
    byfam = {}
    for a in live:
        byfam.setdefault(a.fam, []).append(a)
    for fid in sorted(byfam):
        ms = byfam[fid]; fam = fams[fid]
        if ARM["S"]:
            keepers = [k for k in ms if not _is_scout(k)]
            if keepers:
                for s in sorted((m for m in ms if _is_scout(m) and m.e > HAND), key=lambda z: z.id):
                    over = s.e - HAND
                    for k in sorted((k for k in keepers if k.e < HAND), key=lambda z: (z.e, z.id)):
                        g = min(over, HAND - k.e)
                        if g <= 0: continue
                        k.e += g; s.e -= g; over -= g
                        AR["s_gifts"] += 1; AR["s_given"] += g; _note(k.id, "got_s", g); _note(s.id, "gave_s", g)
                        if over <= 1e-12: break
        if ARM["F"]:
            young = [y for y in ms if _young(y, t)]
            if young:
                for k in sorted((k for k in ms if not _is_scout(k) and not _young(k, t) and k.e > LOW), key=lambda z: z.id):
                    near = [y for y in young if y.e < LOW and _cheb(k.x, k.y, y.x, y.y) <= 1]
                    if not near: continue
                    y = min(near, key=lambda z: (z.e, z.id))
                    g = min(k.e - LOW, LOW - y.e)
                    if g <= 0: continue
                    k.e -= g; y.e += g
                    AR["f_gifts"] += 1; AR["f_given"] += g; _note(y.id, "got_f", g); _note(k.id, "gave_f", g)
        if ARM["H"]:
            for m in ms:
                if m.e > HAND:
                    back = m.e - HAND; m.e = HAND
                    R[m.x, m.y] += back; fam.period_harvest -= back
                    AR["returned"] += back; AR["returned_n"] += 1; _note(m.id, "returned", back)
                if m.e > AR["max_after_cap"]: AR["max_after_cap"] = float(m.e)


def _arm_byfam(live):
    bf = {}
    for a in live:
        bf.setdefault(a.fam, []).append(a)
    return bf


def _arm_with(a, bf, t):
    """True if the young member a spent this move beside (or going to) an adult keeper of its household."""
    best = None; bd = None
    for k in bf.get(a.fam, ()):
        if k.id == a.id or _is_scout(k) or _young(k, t) or not k.alive: continue
        d = _cheb(a.x, a.y, k.x, k.y)
        if bd is None or d < bd or (d == bd and k.id < best.id):
            best, bd = k, d
    if best is None:
        AR["with_no_keeper"] += 1
        return False
    a.target = None; a.run = 0
    if bd > 1: step_toward(a, best.x, best.y)
    AR["with_ticks"] += 1
    return True


'''
swap("class Member:", ARM_CODE + "class Member:")

swap("    global DG; DG = Diag()\n", "    global DG; DG = Diag(); _ar_reset()\n")
swap("        # love: sharing never stops; copying fades with experience (weaning)\n",
     "        if ARM['H'] or ARM['S'] or ARM['F']: _arm_after_eat(live, fams, R, t)\n"
     "        # love: sharing never stops; copying fades with experience (weaning)\n")
swap("        for a in live:\n            out[\"ast\"] += 1; fam = fams[a.fam]\n",
     "        _bf = _arm_byfam(live) if ARM['W'] else None\n"
     "        for a in live:\n            out[\"ast\"] += 1; fam = fams[a.fam]\n"
     "            if _bf is not None and _young(a, t) and _arm_with(a, _bf, t):\n"
     "                DG.mode(a, \"W\"); continue\n")
swap('    seed = int(sys.argv[1]); T = int(sys.argv[2]); outp = Path(sys.argv[3])\n',
     '    seed = int(sys.argv[1]); T = int(sys.argv[2]); outp = Path(sys.argv[3])\n'
     '    for ch in (sys.argv[4] if len(sys.argv) > 4 else "-"):\n'
     '        if ch in ARM: ARM[ch] = True\n')
swap('    Path(str(outp) + ".diag.json").write_text(json.dumps(DG.pack(), separators=(",", ":")))\n',
     '    Path(str(outp) + ".diag.json").write_text(json.dumps(DG.pack(), separators=(",", ":")))\n'
     '    Path(str(outp) + ".arm.json").write_text(json.dumps(dict(arm="".join(k for k in "HSFW" if ARM[k]) or "-", **AR), sort_keys=True))\n')

OUT.write_text(src)
print("wrote", OUT, len(src))
