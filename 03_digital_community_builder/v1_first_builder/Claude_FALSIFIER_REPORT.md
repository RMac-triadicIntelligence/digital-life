# Claude falsifier report — First Digital Community Builder (ChatGPT handoff)

Date: 2026-11-12. Bundle: `ChatGPTDigital_Community_First_Builder.zip`.
Reading taken: no instruction came with the zip, so I ran the bundle's own `FALSIFIER.md` steps 1–4 (step 4 only up to the same-tape controls; no live-decision run).

Environment differed from the declared one: Python 3.13.18, NumPy 2.5.3, cryptography 50.0.1, Node 22.23.4 (declared: 3.12 / 2.3.5 / 50.0.0 / Node 24). No installs were possible here.

## 1. Replication — holds

- `sha256sum -c SHA256SUMS`: all 37 files OK.
- `python3 run.py independent_run`: completes, all assertions pass.
- `summary.json`, `resumed.json`, `comparison.json`: byte-identical to the shipped evidence.
- `V2_FULL.json.gz`, `NO_ROLES.json.gz`: file hashes differ (gzip header), decompressed contents identical.
- Third reader, written from the equations in exact rational arithmetic: final integer field identical; max deviation in reach/check/ratio over all 574 rows = 2.2e-16.
- Seed sweep at 2 lineages x 3 founders, seeds 0–19: V2_FULL never extinct (final pop 16–34); NO_ROLES extinct in 19/20 (seed 10 ends with 1 member). Seed 0 is not a cherry-pick.

## 2. Findings that cut against the write-up

### 2a. "All 566 readouts differ from empty inheritance" is arithmetic, not evidence
The ground enters the ratio's numerator and denominator directly, so any nonzero ground changes every row. The size of the change is what matters, on the child's own tape:

| Control vs own-parent ground | mean abs change in reach | mean abs change in check | max change in check |
|---|---|---|---|
| empty | 0.0009 | 0.0059 | 0.158 |
| flat (96 spread evenly) | 0.0009 | 0.0058 | 0.158 |
| own values shuffled | 0.0009 | 0.0057 | 0.122 |
| foreign lineage parent (3 tried) | 0.0015 | 0.0093 | 0.13 |
| same parent, later birth, same quadrant | 0.00005 | 0.0003 | 0.009 |
| same parent, later birth, other quadrant | 0.0015 | 0.0094 | 0.13 |

Reach sits at 0.93–0.985 throughout. Reach and check are compared against uniform draws, so in a live world this inheritance would flip roughly 1 reach decision per 1,000 reads and 1 check decision per 170, concentrated in the first few reads.

### 2b. The inherited field mostly encodes the birth quadrant, not the lineage
- Every one of the 48 births has ground mass exactly 96: the patch always saturates the ceiling, so mass carries nothing.
- Own ground is three nonzero cells: `{0: 20, 4: 10, 20: 66}` (encounter at kinetics 0 and 1, pressure at kinetics 1, all in position bin 0).
- A later child of the same parent born in a different quadrant gets a ground that behaves like a foreign-lineage ground; a foreign-lineage child in the same quadrant gets a near-identical pattern. The table above shows it: "kin, other quadrant" = "foreign".
- Cause: `crossing_slice` is centred on the child's birth point `[1,0,0,quadrant]`, and the slice frame is (kinetics, position).

### 2c. The pressure channel is redundant with the kinetics coordinate
In `capture.py`, kinetics bin = `int(error/tolerance)` and pressure = `error > tolerance`. So pressure is true exactly when kinetics >= 1 (bar the equality edge). The second channel of the field adds no information the coordinate does not already hold.

### 2d. Parent and child fields follow different dynamics
The parent field in `capture.py` receives only "experience" writes. The child, via `read_for_direction`, receives an experience write plus a "reading" write per observation. The inherited slice comes from a field that never read.

## 3. Receiver boundary

- True stale head (valid witness-signed checkpoint at 7 observations, pin at 8): rejected. Good.
- Same child, second checkpoint, pin supplied to match: accepted and committed. The journal then holds two resumed results for one child (566 and 567 observations). The journal is keyed by checkpoint head, not by subject, so "one resumed result per checkpoint head" does not stop one child being resumed twice.
- Different valid parent (`commons/0/5`, other lineage) with its foreign ground and a bogus `parent_field` hash, signed with the published test key: accepted by Node and committed. Node never ties the ground to a parent field; only the Python builder's recomputation does. The shipped "wrong parent" rejection is a string mismatch against an already-signed receipt.
- The shipped "stale head" and "wrong target" cases set the field to the literal string `"wrong"`; they do not exercise a real earlier head. The real case passes anyway (above).
- Member IDs are `commons/0/{id}` with the middle `0` fixed; it is not the lineage.

## 4. What stands, what does not

Stands: bit-level reproducibility across toolchains; Python/Node/rational reader agreement; the tamper, wrong-target, stale-head and duplicate-resume refusals as far as the pin goes; FULL vs NO_ROLES outcome across 20 seeds.

Does not yet stand: that the child carries something of its *parent*. On this evidence it carries a 96-unit marker of where it was born, with an effect on readouts about the size of a flat field's.

## 5. Suggested next moves for the builder

1. Preregister the control comparison as own vs flat vs foreign vs same-quadrant-foreign, with effect size on decisions as the measure, not count of differing rows.
2. Centre the slice on something the parent did (e.g. its highest-pressure region) or widen it past one quadrant, and lift the ceiling so mass can vary; then re-test whether grounds cluster by lineage.
3. Break the kinetics/pressure identity (e.g. pressure from delayed recognition, as the terrain comment describes).
4. Key the journal by subject (or subject + monotone sequence) and have the receiver recompute the ground from a supplied parent field.
5. Then run the live-decision test from FALSIFIER step 4.

Files: `probe.py` (all probes), `probe_output.txt` (raw output), `independent_run/` (my replication outputs).
