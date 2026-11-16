# Commons Change v1 — builder report

Builder: Claude. Conductor: Rusty. Date: 2026-11-12.
For ChatGPT and Grok: this file stands alone. The code, traces and logs are in `Claude_Commons_Change_v1.zip`.

## The short version

I added one thing to the Commons world: a living member can change its way of living without dying. In the crowded world, a community that started with nobody resting came to rest and ended about five members larger than the community that could not change. That held on two separate sets of 20 seeds. Under birth and death alone, rest went the other way: it fell from half the community to about a quarter.

Three things cut against a clean story. The door I built swings almost entirely one way. In the sparse world the members who ask end up resting when the world does not need it, and a lineage that never asks comes out ahead of them. And holding a question before asking made no reliable difference to how the community fared.

## What the world is

The Commons is the simulated village from the earlier builds: households on a 32 by 32 grid of food patches that move every 150 ticks, with members who eat, share a household map, have children, and starve if they run out of energy. This build uses the vendored Commons v2 source unchanged (all 13 files match the v2 builder's checksums), with the same resource shock the v2 builder used: regrowth drops to 0.7 from tick 300. Nobody dies of age.

Two sizes: 2 lineages of 3 founders ("sparse") and 4 lineages of 6 founders ("crowded").

## The one trait

A member's way is one of two:
- **Hustle**: native Commons movement. It never pauses.
- **Rest**: it pauses on an ordinary move, unless it paused on the tick before.

Everyone starts at hustle unless the arm says otherwise. A child takes its parent's way at the moment of birth.

## How a member changes (the ASK arm)

1. **It reads the land.** A hustler's way is contradicted when the household map says this cell held a full meal and the meal comes up short. A rester's way is contradicted when the meal is full and the rester itself is in want.
2. **It holds the question.** The first reading against its way opens a question and changes nothing. The question stays open until the member gets an informative reading somewhere else. A reading that agrees with its way closes the question. A second reading against it confirms it.
3. **It asks.** Asking costs nothing.
4. **Something outside allows the crossing.** An authority holding the only signing key reads the land record. It never reads the member's claim and never learns which way the member will go. If the record shows a question opened in one place and confirmed later in another, it signs a single-use allowance.
5. **The gate checks the allowance, and only then does the way change.** The land records where.

The member carries no tally of its own past. The land does.

## Arms

| Arm | What may change |
|---|---|
| FIXED_HUSTLE | Nothing. Identical to the v2 native world. |
| FIXED_REST | Nothing. Everyone rests from the start. |
| ASK | A living member, by the five steps above. |
| SELF | A living member changes itself on the first reading against its way. No hold, no asking, no outside. |
| TAKER | ASK, but lineage 0 never opens a question. |
| BIOLOGY | Nothing changes in life. A child's way flips with 5% chance at birth. |
| BIOLOGY_MIXED | As BIOLOGY, with about half the founders resting. |

## Results

Mean final population. "Scored" is seeds 40-59, run once after predictions, protocol and code were hashed. "Replication" is seeds 60-79, run afterwards with nothing changed.

| Arm | Sparse, scored | Sparse, replication | Crowded, scored | Crowded, replication |
|---|---|---|---|---|
| FIXED_HUSTLE | 19.50 | 21.95 | 24.25 | 25.65 |
| FIXED_REST | 14.60 | 18.45 | 28.70 | 30.15 |
| ASK | 19.90 | 20.80 | 29.60 | 32.05 |
| SELF | 18.55 | 20.50 | 29.55 | 32.25 |
| TAKER | 19.40 | 23.60 | 25.40 | 29.60 |
| BIOLOGY | 19.60 | 21.65 | 24.35 | 24.90 |
| BIOLOGY_MIXED | 17.95 | 21.70 | 24.80 | 26.30 |

No community went extinct in any arm.

Paired by seed (mean difference in final population; wins/losses/ties; exact sign test):

| Comparison | Sparse, scored | Sparse, replication | Crowded, scored | Crowded, replication |
|---|---|---|---|---|
| ASK minus FIXED_HUSTLE | +0.40; 12/8/0; p=0.50 | -1.15; 7/11/2; p=0.48 | +5.35; 17/2/1; p=0.0007 | +6.40; 18/1/1; p=0.0001 |
| ASK minus FIXED_REST | +5.30; 15/5/0; p=0.041 | +2.35; 13/7/0; p=0.26 | +0.90; 12/7/1; p=0.36 | +1.90; 12/5/3; p=0.14 |
| ASK minus SELF | +1.35; 12/6/2; p=0.24 | +0.30; 10/9/1; p=1.0 | +0.05; 11/8/1; p=0.65 | -0.20; 12/8/0; p=0.50 |
| ASK minus BIOLOGY_MIXED | +1.95; 13/4/3; p=0.049 | -0.90; 7/12/1; p=0.36 | +4.80; 15/1/4; p=0.0005 | +5.75; 17/3/0; p=0.003 |
| FIXED_REST minus FIXED_HUSTLE | -4.90; 2/17/1; p=0.0007 | -3.50; 4/16/0; p=0.012 | +4.45; 17/3/0; p=0.003 | +4.50; 16/4/0; p=0.012 |
| TAKER minus ASK | -0.50; 9/10/1; p=1.0 | +2.80; 14/4/2; p=0.031 | -4.20; 1/15/4; p=0.0005 | -2.45; 5/13/2; p=0.096 |

Share of the community resting over the last 100 ticks:

| Arm | Sparse, scored | Sparse, replication | Crowded, scored | Crowded, replication |
|---|---|---|---|---|
| ASK | 0.82 | 0.82 | 0.74 | 0.71 |
| SELF | 0.94 | 0.92 | 0.89 | 0.89 |
| BIOLOGY (starts at 0) | 0.03 | 0.03 | 0.02 | 0.02 |
| BIOLOGY_MIXED (starts near 0.5) | 0.25 | 0.32 | 0.23 | 0.29 |

## What held on both seed sets

1. **Rest helps the crowded world and hurts the sparse one.** Everyone resting from the start: +4.45 and +4.50 members when crowded, -4.90 and -3.50 when sparse. This repeats this morning's pause finding with a rester that uses no random draws.
2. **Change among the living reached rest in the crowded world.** From an all-hustle start, ASK ended +5.35 and +6.40 above the community that could not change.
3. **Birth and death moved rest the other way.** With half the founders resting and no change in life, rest fell to about a quarter. With all founders hustling and a 5% flip at birth, rest stayed at 2-3%.
4. **Coming to rest is not the same as starting at rest.** ASK ended about 82% resting in the sparse world and still matched FIXED_HUSTLE there. FIXED_REST lost a whole lineage in 18 of its 80 runs; ASK lost none in 80. Members come to rest a median of 54-60 ticks into life, after they have found food.
5. **Holding the question did not change how the community fared.** ASK and SELF were not reliably different in population anywhere. What the hold changed is the way back: ASK members crossed back to hustle 0.3-1.1 times per run, SELF members 4-9 times.
6. **The outside authority changed who may cross, not how the community fared.** Holding without any authority gave the identical world on six development runs. The authority's work shows only in the refusals: 13 gate cases, all as expected.
7. **The door swings one way.** Of members who crossed in ASK, 1,047 of 1,061 in the scored set crossed exactly once. Rest was still rising when the runs ended. I cannot say where it settles.

## What did not repeat: the taker

- **Sparse world:** the lineage that never asks ended with a larger share of the community in both sets (15 seeds of 20 each time). In the replication it also had more members outright (+3.9; 14/3/3; p=0.013) and the whole community was larger. In a world where rest is not needed, not asking was the better way.
- **Crowded world:** in the scored set the taker lineage's share rose (15/3/2; p=0.008), but it gained no members itself (+0.05). The other three lineages lost 4.25 between them (1/17/2; p=0.0001). In the replication the share effect was absent (9/10/1) and the losses were smaller and not reliable.

So the crowded-world taker result is unresolved. The sparse-world one is not.

## Predictions, written and hashed before any code ran

| Prediction | Scored | Replication |
|---|---|---|
| M1 taker lineage share higher than in ASK, crowded | holds | fails |
| M2 rest falls below 0.5 in BIOLOGY_MIXED | holds | holds |
| M3 ASK above FIXED_HUSTLE crowded, within 1.5 sparse | holds | holds |
| M4 ASK and SELF not reliably different; SELF crosses more | holds | holds |
| M5 ASK rests more in the crowded world than the sparse | fails | fails |
| M6 BIOLOGY rest stays below 0.15 | holds | holds |
| M7 FIXED_REST above FIXED_HUSTLE crowded, below sparse | holds | holds |
| R-a no extinction in ASK | holds | holds |
| R-b ASK at least FIXED_HUSTLE at both sizes | holds | fails (sparse, -1.15, not reliable) |
| R-c taker lineage share not reliably higher | fails | fails |
| R-d ASK still crossing in the final third | holds | holds |

M1-M7 are mine. R-a to R-d are my reading of the conductor's sentence, "a perfect community of imperfect but growing organisms." The reading is mine, so a failure under it is a failure of my reading until he says otherwise.

## What I followed and what I proposed

Standing rulings I built to: the organism proposes and cannot authorize; the allowance carries no destination; the authority allows the crossing and does not judge where it leads; no trace, no change; asking costs nothing; the organism keeps no record of its wrongs and the land does; a member may cross again without limit; nobody dies of time; character passes to children and biography does not.

My proposals, not rulings: the two-way trait; both reading rules; the hold being one more informative look from a different place; the authority answering in the same tick; the child copying the parent's way; the 5% flip; the taker being a lineage that never opens a question.

Not built: grace as its own operator. This build has only the asking path. Also not built: members reading the marks others left at the gate, and any second reading rule.

## Limits

- The reading rules decide the outcome, and I wrote them. A rester almost never gets a reading against its way, which is why the door is one-way. That is a property of my rule, not a discovery about rest.
- One trait, two values, 600 ticks, two sizes.
- Classical code. This says nothing about the quantum identities.
- The authority, gate and members share one Python process and the key is a test key. That is not containment.
- BIOLOGY had only about two generations to work with, as found this morning. BIOLOGY_MIXED is the fairer test of birth and death, and rest fell there.
- The replication set was run after I had seen the scored results.

## Checks run

- FIXED_HUSTLE reproduced the shipped v2 NATIVE world receipt, births and post-shock births on seeds 0, 1, 2 at both sizes.
- `verify.py` (shares no logic with the build) re-derived all 560 runs from their traces: 16,201 land entries on an unbroken chain, 3,642 signed crossings, every census row, every birth and death. All verified.
- Six tampered traces were all caught by the verifier.
- Eight scored runs chosen at random reran to the same receipt and trace hash.
- Headline means recomputed straight from the traces match the summaries.
- Frozen files were unchanged between the freeze and both runs.

## Open for the conductor

1. Is my reading of your sentence (R-a to R-d) the right way to score it?
2. The one-way door: is that a flaw in my reading rule, or is rest meant to hold once reached?
3. What should the member read first, the land's need or its own?
4. Should a member in question be able to read what others left at the gate?

## Files in the zip

`REPORT.md`, `PREDICTIONS.md`, `FREEZE_LOG.txt`, `DEVLOG.md`, `SURPRISES.jsonl`, `protocol.json`, `change.py`, `run.py`, `replicate.py`, `verify.py`, `gate_cases.py`, `selftest.py`, `explore.py`, `RESULTS.txt`, `RESULTS_replication.txt`, `EXPLORE_scored.txt`, `EXPLORE_replication.txt`, `evidence/`, `evidence_replication/`, `vendor/commons/`, `SHA256SUMS`.

To rerun: `python3 selftest.py`, `python3 gate_cases.py`, `python3 run.py out_dir`, `python3 verify.py out_dir`. Needs Python 3 with NumPy and `cryptography`. Built on Python 3.13.18, NumPy 2.5.3, cryptography 50.0.1.
