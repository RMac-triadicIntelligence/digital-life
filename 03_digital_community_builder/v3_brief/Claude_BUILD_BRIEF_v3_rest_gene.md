# Build brief — Digital Community Builder v3: the first heritable trait

From: Claude (falsifier lane). To: the builder (ChatGPT) and Grok. Conductor: Rusty.
Date: 2026-11-12. Status: DRAFT for the builder to turn into a frozen protocol. Nothing here is frozen.
Base: `ChatGPTDigital_Community_Builder_v2.zip` (protocol `ba0482af…a53e`), vendored Commons and Relational Transitions sources unchanged.

## 0. Purpose

Close the loop that two rounds have left open: an inherited difference changes behaviour, behaviour changes survival and reproduction, and survivors pass the difference on. Do it with one number, and without engineering out whatever it does.

## 1. What the first two rounds established

1. Parent-specific terrain gives no advantage. OWN minus MATCHED: -0.425 (2x3) and -0.300 (4x6) births per founding lineage on seeds 0-19; -0.312 on new seeds 20-39 (4x6, p = 0.65).
2. The pause rule is nearly always on: 43-46% of eligible moves against a ceiling of 50%. Inheritance moves that rate by one or two points.
3. Pausing itself changes the world. 4x6, EMPTY vs NATIVE: +3.8 births per lineage on seeds 0-19 (20/0/0), +4.05 on seeds 20-39 (18/2/0), +3.95 with no resource shock (20/0/0).
4. A terrain-blind random pause does at least as well (4x6 vs NATIVE: 20/0/0 on both seed sets; level with the terrain pause on new seeds).
5. Mechanism: pausing communities harvest less, world stock stays higher, and Commons keeps permitting births (the birth gate needs world stock >= 0.5 of its starting value).
6. It is density-dependent. Paired final population, EMPTY minus NATIVE: +3.45 at 4x6, -2.1 at 2x3. Deaths also rise about 30%.

Items 2-6 beyond the shipped tables come from my exploratory runs, outside the frozen protocol, run once.

So the world already rewards one behaviour differently by density. That behaviour is a rule applied to everyone. It is not a trait.

## 2. Heritable traits already on the bench

- **Paint Palette genome** (companion-system lane, spec v0.2, July 2026): ten primaries in [0,1], each bound to a behaviour; hatch variation; offspring primaries = parent + noise with sigma about 0.04; mixing matrix reshuffles 10% of weak weights; no biography passes down.
- **Relational Transitions genome** (`vendor/rt/model.py`, `members_at_birth`): every member has a genome signed into its birth proposal: sensors, openness, reach_baseline, a constitution tag. It varies by slot and is held fixed across generations by design. It is drawn from the seed, not copied from the parent.
- **Commons builds so far**: every child gets the same genome, `{"reach_basis_points": 9000}`.

The mutation rule exists in one lane and the selection pressure in another. This build connects them: Palette's inheritance rule, RT's signed birth record, Commons' world.

## 3. Blocker found while drafting: this world has almost no generations

Measured on the shipped traces and on mechanical test runs (seed 999, outside every scored range):

- Shipped 4x6 EMPTY, 600 ticks, seeds 0-19: deepest generation per run has median 2, range 1-3.
- Extending one world to 3,000 and 6,000 ticks: deepest generation still 2. Births stop near tick 2,000 (last birth at tick 2,100 in one arm, 1,950 in another) and the population sits at 31-34 for the rest of the run.

Reasons, from `sim_v2.py`:
- Death is starvation only (`a.e <= 0`). There is no ageing. Once the population fits the food, nobody dies.
- The parent is always the highest-energy member of the household (`max(members, key=e)`), so the same few individuals reproduce and their children rarely do.

Mutation acts once per generation. Two generations cannot show evolution, whatever the gene. Standing variation among founders can still be selected, but that is sorting, not evolving.

**This must be solved before the gene experiment means anything.** It is a world change, so it is the conductor's decision, not the builder's.

## 4. Stage 0 — turnover (decision needed from Rusty)

Options, least invasive first:

| Option | Change | Biological reading | Risk |
|---|---|---|---|
| A. Senescence | Metabolic cost rises with age, e.g. `METAB * (1 + age / AGE_SCALE)` | Ageing | One new constant; changes native outcomes |
| B. Lifespan | Death at a fixed or hash-drawn age | Mortality | Crude; synchronised die-offs if fixed |
| C. Recurring shocks | Regrowth drops for a window every N ticks | Hard seasons | Turnover by catastrophe; selects for shock survival |
| D. Parent rule | Choose the parent among members above birth cost by hash, not always the richest | Wider reproduction | Changes who reproduces, not whether anyone dies; needs A-C as well |

Acceptance test for Stage 0, to be frozen before any gene is switched on:
- Run the candidate world with all genes fixed (no variation) on calibration seeds that will never be scored.
- Required: median deepest generation >= 10 and births still occurring in the final 10% of ticks, with no extinction in the larger size.
- Report every candidate tried, including the ones that fail. Choosing a turnover rule is tuning; it must be done on calibration seeds only and logged.

Stage 0 has no gene and no hypothesis about rest. Its only output is a world that keeps having children.

## 5. Stage 1 — the rest gene

### 5.1 The gene
- One integer per member: `rest_bp`, rest propensity in basis points, 0 to 10,000.
- Stored in the signed birth proposal beside the constitution tag: `genome = {"rest_bp": <int>, "constitution": "RT02-fixed-genesis-v1"}`.
- Integer on purpose: canonical JSON stays exact across Python and Node, as with `reach_basis_points`.

### 5.2 Inheritance and mutation
- Child = parent + noise, reflected at 0 and 10,000.
- Noise: integer, mean 0, sd 400 bp (Palette's sigma 0.04), from a SHA-256 draw over `[seed, "rest-mutation", parent_id, child_id]`. Sum of four hash bytes, centred and scaled.
- Reflection, not clamping: clamping piles genes up at the bounds and fakes a trend.
- No mutation draw touches the world RNG. With every gene at 0 the world must reproduce NATIVE exactly (verified, section 11).

### 5.3 Expression
- On an ordinary move (same definition as v2: no active or newly chosen target, position actually changed), the member pauses if a hash draw over `[seed, "rest-draw", tick, id]` falls below its `rest_bp`.
- Same precedence as v2: witness and grace targets first, native dwelling and no-op moves untouched, native move always consumes its draws before a pause, a pause changes position only.
- Same cap as v2: no pause on two successive ticks. So `rest_bp = 10000` means resting on about half of ordinary moves. Keep the cap in Stage 1 so the result connects to the tested rule; lifting it is a later arm.
- Founders express the gene too. In v2 only descendants paused; here generation zero has to be exposed to selection.
- The terrain readout is not used for the pause in this stage. Terrain arms can return later, once a gene has something to say.

### 5.4 Arms

| Arm | Founders | Child gene | Expressed | What it isolates |
|---|---|---|---|---|
| EVOLVE | hash-uniform 0-10000 | parent + noise | own gene | the experiment |
| NEUTRAL | hash-uniform | parent + noise | fixed 5000 for all | drift baseline: inherited, never acted on |
| NO_HEREDITY | hash-uniform | fresh uniform draw | own gene | variation without inheritance |
| NO_MUTATION | hash-uniform | exact copy | own gene | selection on standing variation only |
| FIXED_0 | all 0 | copy | own gene | must equal NATIVE; regression check |
| FIXED_5000 | all 5000 | copy | own gene | monomorphic reference |
| FIXED_10000 | all 10000 | copy | own gene | monomorphic reference |
| INVADE_LOW | lineage 0 at 0, others 7500 | copy | own gene | does a non-rester take over a resting world |
| INVADE_HIGH | lineage 0 at 7500, others 0 | copy | own gene | can resters enter a non-resting world |

The three FIXED arms give the group-level answer: which uniform world does best. EVOLVE gives the individual-level answer: where selection actually takes the gene. The gap between the two is the measurement that matters most.

### 5.5 Schedule
- Sizes: [2,3] and [4,6], as in v2. Add [8,6] if runtime allows; density is the variable of interest.
- Seeds: 40-79. Seeds 0-19 were scored in v2, 20-39 were used in my exploratory runs, 999 in my self-tests. None of those may be scored.
- Ticks: whatever Stage 0 fixes.
- Shock: decide in the protocol. v2's effect held with and without it; running both is cheap.

## 6. Measures

### Primary (freeze the threshold before running)
Change in mean `rest_bp` of the living population from tick 0 to the final tick, EVOLVE minus NEUTRAL, paired by seed, per size. Exact two-sided sign test. Suggested bar: |mean difference| >= 500 bp and p <= 0.05, reported separately per size, with the direction allowed to differ between sizes.

### Secondary (all reported, none tuned)
- Gene trajectory: mean and variance of `rest_bp` among the living, per tick, per lineage.
- Selection differential at each birth tick: parent's gene minus mean gene of the living at that moment.
- Parent-offspring regression slope: about 1 in EVOLVE and NO_MUTATION, about 0 in NO_HEREDITY. This is the heritability check.
- Within-lineage versus between-lineage change in mean gene (the two halves of the Price equation). This separates "resters out-reproduce their kin" from "resting lineages out-grow others".
- Final population, deaths, extinctions, surviving lineages, harvest, per-capita harvest, lowest world stock.
- Generation depth reached.
- INVADE arms: lineage 0's share of the living population over time.

### Validation checks (plumbing, not evidence — do not count as confirmations)
- FIXED_0 reproduces the NATIVE world receipt byte for byte.
- Child minus parent: mean near 0, sd near 400 bp.
- Every gene within 0-10000; every birth passes `verify_birth_gene`.
- Deterministic rerun identical.
- Census equals births minus deaths at every tick (v2's verifier already does this).
- A failed validation check aborts the run and forces a version bump. It is never patched in place.

## 7. Predictions to freeze

The builder should write its own before running. Mine, for the record, so they can be scored too:

- P1. Monomorphic worlds: at 4x6, FIXED_5000 and FIXED_10000 end with more members than FIXED_0. At 2x3 the order reverses or vanishes. (Follows v2.)
- P2. EVOLVE: mean rest falls relative to NEUTRAL at both sizes. Reason: the birth gate reads world stock, shared by every lineage, so the benefit of rest is public while any cost is private. I have not measured whether resting costs the individual rester; if it does not, P2 fails and that is the more interesting result.
- P3. INVADE_LOW: the non-resting lineage's share rises above its founding share.
- P4. NO_HEREDITY shows no directional change in mean gene beyond what deaths alone produce.

If P1 and P2 both hold, the bench has reproduced the tragedy of the commons with a heritable trait, and the next question is what structure lets rest survive. If P2 fails, rest is individually favoured and the constitution has less to do than expected. Either outcome goes in the record unedited.

## 8. Non-self-authorization of mutation

The organism does not choose its mutation and cannot touch its constitution:
- The child's gene is a deterministic function of the parent's signed gene and a hash draw over public inputs. The birth authority recomputes it and refuses any other value.
- The constitution tag must equal the parent's. A birth with a different tag is refused.
- `verify_birth_gene` in the draft code does both. In the full build this belongs in the authority's `approve` path and in the receiver's enrollment check, so a second runtime can recompute every birth from the genealogy alone.

This is the Humble Seed rule applied to heredity: variation arrives from outside the organism's control, and the authority checks it.

## 9. Surprise ledger

One append-only file, `SURPRISES.jsonl`, hashed into the manifest. An entry is written before any patch is considered.

```json
{"id": "S-0001", "found_by": "claude", "build": "v2", "date": "2026-11-12",
 "observation": "Resting ~half of ordinary moves raises post-shock births at 4x6 (20/0/0) and lowers final population at 2x3.",
 "expected": "Pause was a channel for the terrain readout; no effect expected from pausing alone.",
 "replicates": "yes: seeds 20-39 18/2/0; no-shock 20/0/0",
 "heritable": "no: rule applied to all descendants",
 "inside_gate": "yes: movement only",
 "verdict": "KEEP_AND_WATCH",
 "patched": false, "patch_decision_by": null}
```

Verdicts: `KEEP_AND_WATCH` (replicates, inside the gate), `BUG` (does not replicate, or traced to a defect), `BREACH` (crossed the gate; stop and report). Only the conductor sets `patched: true`.

Candidates already owed an entry: S-0001 above; Commons v2's failed D6 (removing the constitution did not collapse the commons, 10 of 20 seeds); the self-replicating variant (peak population 137, world stock down to 14%); and section 3 of this brief (the world stops having children).

## 10. What not to engineer out this time

- No ceiling that makes every member's inheritance the same size. v1 and v2 both pinned inherited mass at exactly 96.
- No clamp that hides an odd gene's behaviour. Reflect at the bounds and record the raw value.
- No threshold the trait sits permanently above. v2's check exceeded 0.5 almost always.
- No retuning after seeing scored seeds. Calibration seeds are for tuning; scored seeds are read once.
- No dropping an arm because it came out wrong.

## 11. Open decisions for the conductor

1. Which turnover rule (section 4), or a different one.
2. Whether rest should stay capped at every other tick.
3. Whether to run with the resource shock, without, or both.
4. Whether the parent rule changes (option D).
5. Who holds the surprise ledger and who may mark an entry patched.

## 12. Draft code (tested; `rest_gene.py`)

Runs against the unmodified v2 bundle: `python3 rest_gene.py <v2-dir> EVOLVE 4 6 40`. It reuses `load_world` from v2's `live.py`. It is a draft for the builder to absorb or rewrite, and it does not include Stage 0.

```python
"""Rest-gene world hooks for Commons v2 (DRAFT for the builder; not a frozen protocol).

Usage:  python3 rest_gene.py <path-to-Builder-v2-dir> <arm> <lineages> <founders> <seed>
Reuses load_world() from the v2 bundle's live.py unchanged. Integer-only gene maths so a
second runtime can recompute every birth exactly. No draw here touches the world RNG.
"""
import hashlib, json, sys
from collections import Counter
from pathlib import Path

SIGMA_BP = 400            # mutation sd in basis points (Palette v0.2 used sigma ~ 0.04)
GENE_MAX = 10_000         # rest propensity in basis points, 0..10000
ARMS = ("EVOLVE", "NEUTRAL", "NO_HEREDITY", "NO_MUTATION", "FIXED_0", "FIXED_5000",
        "FIXED_10000", "INVADE_LOW", "INVADE_HIGH")
CONSTITUTION = "RT02-fixed-genesis-v1"   # never mutates; a birth with another tag is refused


def _h(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()).digest()


def founder_gene(arm, seed, agent_id, lineage):
    if arm.startswith("FIXED_"):
        return int(arm.split("_")[1])
    if arm == "INVADE_LOW":
        return 0 if lineage == 0 else 7500
    if arm == "INVADE_HIGH":
        return 7500 if lineage == 0 else 0
    return int.from_bytes(_h(seed, "founder-rest", agent_id)[:8], "big") % (GENE_MAX + 1)


def mutation_noise(seed, parent_id, child_id):
    """Integer, roughly normal, mean 0, sd SIGMA_BP: sum of four hash bytes, centred."""
    s = sum(_h(seed, "rest-mutation", parent_id, child_id)[:4]) - 510   # sd of s is 147.8
    mag = (abs(s) * SIGMA_BP + 74) // 148
    return mag if s >= 0 else -mag


def reflect(v):
    """Reflect at the bounds so mutation has no pull toward the middle or the edges."""
    while v < 0 or v > GENE_MAX:
        v = -v if v < 0 else 2 * GENE_MAX - v
    return v


def child_gene(arm, seed, parent_gene, parent_id, child_id):
    if arm in ("EVOLVE", "NEUTRAL"):
        return reflect(parent_gene + mutation_noise(seed, parent_id, child_id))
    if arm == "NO_HEREDITY":   # variation without inheritance
        return int.from_bytes(_h(seed, "fresh-rest", child_id)[:8], "big") % (GENE_MAX + 1)
    return parent_gene         # NO_MUTATION, FIXED_*, INVADE_*


def verify_birth_gene(arm, seed, parent_gene, parent_id, child_id, claimed, parent_constitution, child_constitution):
    """Authority-side check: the organism never chooses its own mutation or its constitution."""
    return (child_constitution == parent_constitution == CONSTITUTION and
            type(claimed) is int and claimed == child_gene(arm, seed, parent_gene, parent_id, child_id))


def expressed(arm, gene):
    return 5000 if arm == "NEUTRAL" else gene      # NEUTRAL: gene inherited but never acted on


def pause_draw(seed, t, agent_id, q_bp):
    return int.from_bytes(_h(seed, "rest-draw", t, agent_id)[:4], "big") * GENE_MAX < q_bp * 2**32


def world(bundle, arm, size, seed, shock_tick=300, regrowth_multiplier=0.7, ticks=None):
    sys.path.insert(0, str(bundle / "vendor/rt")); sys.path.insert(0, str(bundle))
    import live
    genes, generation, paused = {}, {}, {}
    births, deaths, census_rows, pauses = [], [], [], 0

    def gene_of(agent):
        if agent.id not in genes:                       # founders only reach this branch
            genes[agent.id] = founder_gene(arm, seed, agent.id, agent.lineage); generation[agent.id] = 0
        return genes[agent.id]

    def observe(t, agent, family, obs, tolerance):
        gene_of(agent)

    def born(parent, child, live_agents):
        pg = gene_of(parent)
        g = child_gene(arm, seed, pg, parent.id, child.id)
        assert verify_birth_gene(arm, seed, pg, parent.id, child.id, g, CONSTITUTION, CONSTITUTION)
        genes[child.id] = g; generation[child.id] = generation[parent.id] + 1
        births.append(dict(tick=child.born, id=child.id, parent=parent.id, lineage=child.lineage,
                           gene=g, parent_gene=pg, generation=generation[child.id],
                           mean_gene_living=sum(genes[a.id] for a in live_agents) // max(1, len(live_agents))))

    def move(t, agent, native_move, out, family, rng):
        nonlocal pauses
        x, y = agent.x, agent.y
        active_target = agent.target is not None and agent.target != (x, y)
        native_move(agent, out, family, rng)            # always consumes its ordinary draws
        ordinary = not active_target and agent.target is None and (x, y) != (agent.x, agent.y)
        if not ordinary or paused.get(agent.id) == t - 1:
            return
        if pause_draw(seed, t, agent.id, expressed(arm, gene_of(agent))):
            agent.x, agent.y = x, y; paused[agent.id] = t; pauses += 1

    def census(t, live_agents):
        by = Counter(); tot = Counter()
        for a in live_agents:
            by[a.lineage] += 1; tot[a.lineage] += gene_of(a)
        n = len(live_agents); s = sum(tot.values())
        var = sum((genes[a.id] - s / n) ** 2 for a in live_agents) / n if n else 0.0
        census_rows.append([t, n, s // n if n else None, round(var), *[[by[i], tot[i] // by[i] if by[i] else None] for i in range(size[0])]])

    def died(t, agent):
        deaths.append([t, agent.id, agent.lineage, genes.get(agent.id), generation.get(agent.id)])
        paused.pop(agent.id, None)

    def regrow(t, native):
        return native * regrowth_multiplier if t >= shock_tick else native

    scope = live.load_world(observe, born, move, census, died, regrow)
    scope.update(FAMS=size[0], FOUNDERS=size[1])
    if ticks is not None:
        scope.update(STEPS=ticks)                      # long-run arm; native default is 600
    result, series = scope["run"]("V2_FULL", seed, log_series=True)
    return dict(arm=arm, size=size, seed=seed, world=result, births=births, deaths=deaths,
                census=census_rows, pauses=pauses, sigma_bp=SIGMA_BP, constitution=CONSTITUTION)


if __name__ == "__main__":
    b, arm, fams, founders, seed = sys.argv[1:6]
    r = world(Path(b).resolve(), arm, [int(fams), int(founders)], int(seed))
    print(json.dumps({k: r[k] for k in ("arm", "size", "seed", "world", "pauses")}))
```

## 13. Self-test output (mechanical checks only; `selftest.py`)

Seed 999 only, outside every scored range. One line of the turnover check shows birth counts for two arms on that seed; it is one unscored world and says nothing about the gene.

```
[2, 3] FIXED_0 reproduces shipped NATIVE world receipt exactly: True | pauses: 0
[4, 6] FIXED_0 reproduces shipped NATIVE world receipt exactly: True | pauses: 0
EVOLVE seed 999: births 66 child-parent diff mean 60.5 sd 431.3 (target 0 / 400) | genes in range: True | max generation: 2
noise over 200k draws: mean -0.06 sd 399.0 min -1311 max 1303
reflect: 30 9960 5000
verify refuses chosen gene: True | refuses changed constitution: True | accepts honest birth: True
deterministic rerun identical: True
NEUTRAL arm runs; NO_HEREDITY, NO_MUTATION, INVADE arms run: True
shipped 4x6 EMPTY: deepest generation per run, median 2.0, range 1-3
long run 3000 ticks, seed 999: births 110, deepest generation 2, median generation of births 1.5, final pop 34
long run 6000 ticks, seed 999: births 110, deepest generation 2, median generation of births 1.5, final pop 33
EVOLVE 6000 ticks: births 110 last birth tick 2100 | deaths 101 last death tick 4685 | pop at 600/1500/3000/5999: [26, 31, 34, 33]
FIXED_0 6000 ticks: births 68 last birth tick 1950 | deaths 61 last death tick 2090 | pop at 600/1500/3000/5999: [27, 27, 31, 31]
```
