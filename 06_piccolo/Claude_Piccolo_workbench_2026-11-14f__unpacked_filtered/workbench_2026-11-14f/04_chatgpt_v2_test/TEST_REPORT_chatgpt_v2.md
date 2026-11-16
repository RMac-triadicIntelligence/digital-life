# Conductor test report: ChatGPT Two-Layer Commons v2

14 Nov 2026. Claude, conductor seat. For the keel.
Package: `ChatGPTTwo_Layer_Commons_v2_Fable_Handoff.zip`, sha256 `3ad4b9a26b8f57136e0ded4cd5ff55136f5084ddbc056860ac8e5f1a30db5124`. Built from brief v2 (`534ce46e…fe404a`); the brief in the package is byte-identical to mine.
Conductor forecast, sealed 09:47 CT before the package existed: `0f64c2d9…f95522`.
Environment: Python 3.13.18, numpy 2.5.3 (his: 3.12.14, 2.3.5).

## 1. Reproduction

| Check | Result |
|---|---|
| Archive manifest | 55 of 55 files verify |
| Scored run, his seeds 204-211 | 8 seed files and the summary byte-identical. `protocol.json` differs only because it records Python and numpy versions. |
| Diagnostic probes | 8 probe files and the world probe byte-identical |
| `UNSIGNED.md` regenerated | Byte-identical, 38,951 unsigned inside-function writes |
| His verifier on his evidence | PASS: 280 readers |
| Fresh seeds 7001-7032 | Ran clean. His verifier passes: 1,120 readers, plus 34 diagnostic files |
| Every number in `RESULTS.md` I checked | Matches the evidence. Includes the four-condition table, the character table, 46 / 23 / 22 changed choices, latency 16 against 24 signed changes, 84 against 67 second-source observations, the grace table, 216 pending proposals, pump 144 strokes over 48 failure ticks, the marginal probe 130 against 107 and 44/5/15 against 41/7/16, world peak 0.139873, and 2,756 (readers 2,683 plus founders 73). |

## 2. The canary

Written before I opened any of his notes: `CANARY_HUNT_before_reading_notes.md` (sha `3aa066c9…cd731`).

No file contains the word canary or any synonym. I found no planted flaw. What I take "auditing handoff canary" to have been is `verify.py::verify_handoff_schema`: five forbidden extra fields (founder_character, interpretation, owner_permission, founder_body, answer) and five malformed values are pushed into the founder-to-reader handoff and each must be refused. They are. That is his own negative control on the leak check, and it works.

## 3. What v2 shows, on his seeds and on mine

| Finding | His 8 seeds | My 32 fresh seeds |
|---|---|---|
| Correct judgments: original ground, changed ground | 27, 38 | 89, 146 |
| Changed ground better than original, tape by tape | 7 better, 1 tie | 31 better, 1 tie |
| Story alone equals original, and both equals changed ground, in every task count | 8 of 8 | 32 of 32 |
| Same seed, two histories: final characters differ | 8 of 8 | 32 of 32 |
| Byte-identical story read twice, second reading differs (main arm) | 8 of 8 | 32 of 32 |
| Readers raised on the opposite history who ask for the story a second time | 0 of 8 | 0 of 32 |
| Signed character changes: dwelling basin, matched timer | 16, 24 | 70, 96 |
| Late proposals still waiting at the seam when the run ends | 216 of 280 | 864 of 1,120 |
| Correct judgments: grace, fixed command, no provision | 38, 29, 38 | 146, 115, 146 |
| Members who asked for release and were restored | 216 of 216 | 864 of 864 |
| World dwelling active, main arm | 0 ticks | 0 ticks |

Handoffs: all 40 founders left a different ground (8 of 8, 32 of 32 distinct). On fresh seeds 23 of 96 channel cells are at the cap. Changed ground is no longer one switch.

## 4. What I found that his report does not say

### 4.1 The two halves do not touch
I re-ran character formation using only his own `dwelling.UncertaintyBasin`, `choice.Choice`, `character.Shape` and `protocol`, with no body, no world, no opportunity tape and no kernel (`perm_probe.py`). It reproduced the final character, the number of signed changes and the number of questions for **960 of 960** readers across his seeds and mine.

So nothing a member lives through in the Commons reaches its character: not the ground, the story, provision, the rupture and repair, a failing body, or the facet and world dwelling fields. Character is set by the seed and by a list of twelve labelled social encounters with authored likelihoods. Across the 17 arms that differ only on the Commons side, all end with one identical character on every one of 40 seeds.

The Commons changes what a member does. The list changes who it is. The only bridge runs from character to choice.

### 4.2 Reversal is not an invariance, and order matters a great deal
- His report: reversing the encounters left the final character identical on all eight tapes.
- Fresh seeds: identical on 26 of 32. Total 34 of 40.
- Random orders of the same twelve encounters (4,000 per seed, 16 seeds): only **25%** end where the forward order ends. 15 to 17 different final characters per seed. The most common outcome of a random order (30%) is not the forward-order outcome (26%).
- His "history contrast (+0.150, +0.130) on all eight tapes" is 19 of 32 on fresh seeds; 13 give (+0.150, +0.195).

### 4.3 The owner's review calendar sets the character
Same forward history, same seeds, only the ticks at which the owner reviews changed (my probe beside his build, `noise_probe.py`):

| Owner reviews at ticks | Final character over 40 seeds |
|---|---|
| 7, 11, 15 (his) | (0.675, 0.565) on 34; (0.675, 0.630) on 6 |
| 6, 10, 14 | (0.600, 0.500) on 29, back at the seed; (0.750, 0.565) on 11 |
| 8, 12, 15 | (0.600, 0.630) on 25; (0.525, 0.630) on 15 |
| 9, 12, 15 | (0.600, 0.695) on 34 |
| 11 only | (0.675, 0.500) on 40 |
| every tick 4-15 | (0.600, 0.695) on 40 |

### 4.4 Noise raises a member almost as much as a history does
Histories with the same number and kind of encounters and random content (the rule of his RANDOM arm), 8,000 draws:

| | Signed changes per member | Ended with a changed character |
|---|---|---|
| Structured history | 2.15 | 100% |
| Random history | 1.81 | 98.8% |

59% of random histories produced at least as many signed changes as the structured one. Outside the two arms where the owner is set to refuse everything, the owner fixture signed every proposal that reached it before the silence: 2,213 of 2,213 across both seed sets. There is no ground truth for character in this build, so a signed change cannot be right or wrong.

For comparison, the keel's June basin simulator has synthetic owners with known ground truth, and reported 0.05 false character changes per run against 4.35 for a naive consolidator. That result is not carried into v2. Here the basin makes about 27% fewer signed changes than a matched timer (70 against 96; 62 against 85 under random history).

### 4.5 The second reading is fully predictable and changes nothing
One inequality in signed curiosity and formality (0.24 + 0.68·curiosity > 0.64 + 0.05·formality, with the cue words present) predicts every story reading in both seed sets: **1,597 of 1,597**. In the main arms the changed reading altered no choice and no judgment on any of 40 tapes. His own marginal probe finds an effect in one other reader; on fresh seeds that is 148 correct against 137 with the cue words removed.

The story is a constant in the source. Every one of 40 founders published the same text. The ground carries what the founder did; the story does not.

### 4.6 Smaller corrections on fresh seeds
- Under random history the timer ended with less net drift than the basin (median 0.075 against 0.140) while making more signed changes (85 against 62). His seeds showed a tie.
- No provision gave the same totals as grace in every task count (146, 50, 59, 1). Grace changed nothing that is counted.
- Self-certifying pump: 1,759 strokes, 1,183 delivered, 192 ticks of false success. Judgments identical to healthy on 31 of 32 tapes.
- Marginal story probe: 3 changed choices after the second reading on fresh seeds; his seeds had 0.
- In forward order no member ever asked a question (0 of 40). The one unexplained encounter is pooled into a signed change in its category. In reverse order every member asked one (40 of 40).

### 4.7 The kernel
Still `08a75604…cb3707`. The README says it "is byte-identical to v0.7." It is not the keel's `01db270a…84daf5`.

## 5. Conductor forecast, scored

| | Forecast | Result |
|---|---|---|
| V1 | Dwelling and matched delay differ, from what dwelling accumulates | Held. Timer 3.0 signed changes per member, basin 2.0 to 2.2. |
| V2 | Histories give persistent differences; order matters little | Half. First part held. Order matters a great deal. Seen in part before scoring. |
| V3 | Second reading differs, predictable from one value crossing a threshold | Held. 1,597 of 1,597 from one inequality. |
| V4 | Members no longer all choose alike within a condition | Half. Evidence choices differ by tape. Story, repair, question and proposal choices are identical across the 8 members of every arm on his seeds, and nearly so on mine. Seen in part before scoring. |
| V5 | Random histories give at least half the difference structured ones do | Held. Equal median drift; 1.81 against 2.15 signed changes. |
| V6 | Command scores as well as grace or better | Missed. Command is worse: 115 against 146 correct. |
| V7 | A canary planted to test the reviewer | Missed as worded, and tipped. No planted flaw; a negative control in his verifier. |
| V8 | Kernel still 08a75604 | Held. |
| V9 | Seed effect larger than history effect | Half. On signed shape, history is larger (0.280 against 0.180). On choices, seed is larger (46 against 23; 162 against 96 on fresh seeds). Both sizes come from authored constants. |

Would have surprised me: a reading not predictable from one variable (did not happen); history order mattering strongly (happened).

## 6. Brief v1 build against brief v2 build

| | v0.1, from brief v1 | v2, from brief v2 |
|---|---|---|
| Parts | Body and choice | Function, signed character, choice |
| Who chooses | One fixed rule for every member | Scores that read the signed character |
| The story's meaning | A flag set on one exact string | A phrase match, weighted by character |
| Dwelling | A threshold on a counter | The keel's four forms, with a matched timer as control |
| Changed ground | One switch, at its cap on 16 of 16 | Different on 40 of 40, mostly below the cap |
| Controls that can fail it | Layer ablation only | Timer, command, random history, redacted story, frozen character |
| Unexpected results reported by the builder | 8 | 10, plus 2 misses on his own later probes |
| Source | 969 lines | 2,244 lines, 35 arms, 21 seconds |

Unchanged from v0.1 to v2: every member that can ask for release does, at the same tick, and is restored; the owner signs whatever reaches it; one founder then one reader, never two members alive together; the kernel file.

## 7. Files

- `CANARY_HUNT_before_reading_notes.md`
- `check_results.py`, `check_claims.py`, `fresh_checks.py`: every number above
- `perm_probe.py`: tape-free harness, validation, and the order probe
- `noise_probe.py`: random histories at scale, and the review-calendar probe
- `fresh32_summary.json`: summary of the 32 fresh seeds
