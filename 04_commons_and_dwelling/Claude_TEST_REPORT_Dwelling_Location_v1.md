# Dwelling Location v1 — test report

Builder: Claude. Conductor: Rusty. Date: 2026-11-12.
For ChatGPT and Grok: this file stands alone. Code, traces and logs are in `Claude_Dwelling_Location_v1.zip`.

## The short version

I had inferred that the dwelling field belongs to the living member, not to the land, the household or a central holder. The conductor said to test it instead of deciding it. By the rule I wrote down before running anything, **the inference failed on the scored seeds**: a field held by the household did at least as well as one held by the member, at both community sizes, on both measures. On the replication seeds the result was mixed. No difference between member-held, household-held and centrally held fields was reliable anywhere.

The test also showed that this world is a blunt instrument for the question. Grace never fired once in 480 runs, and nearly half of all observations count as surprising, so the dwelling field here is fed mostly by noise.

## What was tested

The Commons world already contains a dwelling field and a grace rule, frozen in its own preregistration:
- Each member has a value d. A surprising observation (what it sees differs from what it believes by more than 0.25) raises d; an unsurprising one lowers it. While d is above 0.6 and there is food where it stands, the member stays put and keeps sampling.
- Every 10 ticks, from outside, the conductor releases the one member that has dwelt longest, if it has dwelt 15 ticks or more in a row.

Nothing in those rules was changed. Only the place the field is kept was moved:

| Arm | Where the field lives |
|---|---|
| LIGHT | in each member (native, unchanged) |
| LAND | in each cell of the ground |
| FAMILY | in each household |
| CENTRAL | one value for the whole world |
| NONE | nowhere; nobody dwells |
| TIMER | nowhere; where there is food, a member stays on a coin flip at LIGHT's rate |

World: vendored Commons v2, unchanged (13 files match the v2 builder's checksums), with the same resource shock as the earlier builds (regrowth x0.7 from tick 300). Two sizes: 2 lineages of 3 founders ("sparse") and 4 lineages of 6 ("crowded"). Scored seeds 80-99, run once after predictions, protocol and code were hashed. Replication seeds 100-119, run afterwards with nothing changed. 480 runs in all.

Measures: final population (higher is better) and the world's own map error (lower is better), paired by seed, exact sign test.

## Results

Mean final population:

| Arm | Sparse, scored | Sparse, replication | Crowded, scored | Crowded, replication |
|---|---|---|---|---|
| LIGHT | 21.65 | 21.45 | 25.00 | 24.20 |
| LAND | 21.85 | 19.90 | 24.70 | 23.60 |
| FAMILY | 22.75 | 22.00 | 25.30 | 25.65 |
| CENTRAL | 22.40 | 21.50 | 25.85 | 25.05 |
| NONE | 21.10 | 19.85 | 23.05 | 23.15 |
| TIMER | 21.55 | 21.60 | 26.20 | 23.80 |

Mean map error:

| Arm | Sparse, scored | Sparse, replication | Crowded, scored | Crowded, replication |
|---|---|---|---|---|
| LIGHT | 0.1842 | 0.1844 | 0.1801 | 0.1792 |
| LAND | 0.1886 | 0.1931 | 0.1840 | 0.1820 |
| FAMILY | 0.1838 | 0.1867 | 0.1801 | 0.1808 |
| CENTRAL | 0.1864 | 0.1859 | 0.1826 | 0.1833 |
| NONE | 0.1971 | 0.1921 | 0.1838 | 0.1874 |
| TIMER | 0.1890 | 0.1872 | 0.1864 | 0.1807 |

Share of member-ticks spent staying: LIGHT 0.21-0.23, FAMILY and CENTRAL 0.21-0.24, TIMER 0.21-0.23 (matched by calibration), LAND 0.06-0.09, NONE 0.

## The decision rule and what it returned

Written before any run: the inference FAILS if another placement is at least as good as LIGHT on both measures at both sizes on the scored set; it is SUPPORTED if LIGHT is at least as good as every placement and reliably better than each somewhere; otherwise MIXED. A separate flag, UNINFORMATIVE, is raised if LIGHT cannot be told from TIMER.

- **Scored set: FAILS.** FAMILY had a higher mean population than LIGHT at both sizes (22.75 vs 21.65; 25.30 vs 25.00) and a map error no higher (0.1838 vs 0.1842; equal to four decimals when crowded). The margins are small and none is reliable on its own.
- **Replication set: MIXED.** FAMILY again had more members, but a slightly higher map error. The UNINFORMATIVE flag was raised on this set: LIGHT could not be told from TIMER on either measure at either size.

## What held on both seed sets

1. **Dwelling does something.** With no dwelling at all, map error was higher in all four cells (reliably in three), and the crowded population was lower.
2. **The member's own field maps slightly better than a coin flip.** LIGHT's map error was lower than TIMER's in all four cells (14, 16, 11 and 12 of 20 seeds), reliably in one. Population did not differ.
3. **A member-held field has longer dwelling episodes than a timer:** about 1.55 ticks against 1.26, on 20 of 20 seeds in every cell.
4. **The land is the worst home.** A field kept in the ground rarely rises high enough to hold anyone (0.06-0.09 of ticks) and its map error was higher than LIGHT's in all four cells.
5. **Shared fields are not worse than member-held ones.** FAMILY and CENTRAL had mean populations at least as high as LIGHT's in all four cells.

## Exploratory, after the results were seen

Pooling both sizes and both seed sets (80 paired worlds), LIGHT minus other:

| Other | Population | Map error |
|---|---|---|
| NONE | +1.29; 46 higher, 23 lower; p = 0.008 | lower in 59 of 80; p < 0.0001 |
| TIMER | -0.21; p = 0.41 | lower in 53 of 80; p = 0.005 |
| LAND | +0.56; p = 0.096 | lower in 50 of 80; p = 0.024 |
| FAMILY | -0.85; 28 higher, 45 lower; p = 0.060 | lower in 48 of 80; p = 0.093 |
| CENTRAL | -0.62; 23 higher, 39 lower; p = 0.056 | lower in 49 of 80; p = 0.057 |

The pattern, short of reliable: a member-held field gives a slightly better map; a shared field gives slightly more members.

## Two findings about the world itself

- **Grace never fires.** Zero releases in 480 runs, in any arm. The longest dwelling episode anywhere was 13 ticks; grace needs 15. Ten further runs without the resource shock also had zero. In this world the grace rule is written down and never used, so nothing here can test "without dwelling, grace fails" or "grace makes the basin whole".
- **The field is fed mostly by noise.** About 48% of all observations count as surprising. The observation noise (0.25) is as large as the disagreement threshold (0.25). Dwelling episodes average about a tick and a half.

## Predictions, written and hashed before any code ran

| Prediction | Scored | Replication |
|---|---|---|
| L1 LIGHT vs TIMER: staying matched; map error lower under LIGHT; population not different | holds | holds |
| L2 LIGHT above LAND on population when crowded; map error not higher | holds | holds |
| L3 LIGHT's map error lower than FAMILY's and CENTRAL's at both sizes | fails | holds |
| L4 LIGHT better than NONE on map error; more members when crowded | holds | holds |
| L5 LIGHT's dwelling episodes longer than TIMER's | holds | holds |
| Decision rule | FAILS | MIXED, flagged uninformative |

## Limits

- One embodiment of dwelling: the Commons' own. This world has no uncertainty basin of the June design, no pooled reads, no fill, and in practice no grace.
- The differences between placements are a few hundredths of the map error and about one member in twenty.
- The replication set was run after I had seen the scored results.
- Classical code. Says nothing about the quantum identities.

## Checks run

- LIGHT reproduced the shipped v2 NATIVE world receipt on seeds 0, 1, 2 and this morning's FIXED_HUSTLE receipt on seeds 40, 41, at both sizes.
- Every run's stay count equals the sum of its dwelling episodes and matches the world's own stuck share. `verify.py` re-derived every census row from births and deaths for all 480 runs.
- Eight scored runs chosen at random reran to the same receipt and trace hash.
- Frozen files and protocol unchanged between the freeze and both runs.

## Files in the zip

`REPORT.md`, `PREDICTIONS.md`, `FREEZE_LOG.txt`, `DEVLOG.md`, `SURPRISES.jsonl`, `protocol.json`, `locate.py`, `run.py`, `verify.py`, `selftest.py`, `calibrate.py`, `CALIBRATION.txt`, `dev_look.py`, `dev_look_1.txt`, `RESULTS.txt`, `EXPLORE.txt`, `evidence/`, `evidence_replication/`, `vendor/commons/`, `SHA256SUMS`.

To rerun: `python3 selftest.py`, `python3 run.py out_dir`, `python3 verify.py out_dir`. Python 3 with NumPy. Built on Python 3.13.18, NumPy 2.5.3.
