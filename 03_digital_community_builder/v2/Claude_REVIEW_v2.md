# Claude review + blue sky — Digital Community Builder v2 (ChatGPT build)

Date: 2026-11-12. Bundle: `ChatGPTDigital_Community_Builder_v2.zip`.
Environment: Python 3.13.18, NumPy 2.5.3, cryptography 50.0.1, Node 22.23.4 (declared: 3.12 / 2.3.5 / 50.0.0 / Node 24; no installs possible here).

## 1. Replication — holds completely

- `sha256sum -c SHA256SUMS`: 283 of 283 OK. `protocol.json` matches `protocol.sha256`.
- `verify_live.py evidence/live`: 240 traces and 12 unshocked native references verified.
- Fresh 240-run execution: both receipts byte-identical, all 240 decompressed traces identical.
- `receiver_demo.py`: all 11 cases reproduce; summary identical to the shipped one.
- Vendored Commons and RT sources are identical to the first build's.

## 2. The primary result is an honest null, and it replicates

OWN minus MATCHED: -0.425 (2x3) and -0.300 (4x6) births per founding lineage, as reported.
On 20 new seeds (20-39, 4x6, my run): -0.312, W/L/T 11/8/1, p = 0.65. Own-parent terrain still gives no advantage over a same-quadrant stranger's.

## 3. What the traces show beyond the write-up

### 3a. The pause rule fires almost every time it is allowed
The rule allows a pause at most every other tick, so the ceiling is 0.5 of eligible moves.

| Arm | 2x3 pause rate | 4x6 pause rate |
|---|---|---|
| OWN | 0.457 | 0.436 |
| MATCHED | 0.447 | 0.435 |
| FLAT | 0.446 | 0.430 |
| EMPTY | 0.435 | 0.428 |
| LEGACY | 0.465 | 0.449 |

Median check at a pause is about 0.545 against a threshold of 0.5. The readout sits above the threshold nearly all the time, so the rule is close to "move at half speed". Inheritance shifts the pause rate by about 1-2 points. There is almost nothing for a parent-specific signal to act through.

### 3b. A terrain-blind coin flip does as well as the terrain readout (exploratory, my runs)
New arm RANDPAUSE: empty ground, pause decided by a hash draw (q = 0.75) under the same every-other-tick rule, giving a similar pause count.

| 4x6 comparison | post-shock births per lineage | paired W/L/T | p |
|---|---|---|---|
| RANDPAUSE vs NATIVE, seeds 0-19 | 8.13 vs 2.84 | 20/0/0 | 1.9e-06 |
| RANDPAUSE vs EMPTY, seeds 0-19 | 8.13 vs 6.64 | 12/4/4 | 0.077 |
| RANDPAUSE vs OWN, seeds 0-19 | 8.13 vs 6.58 | 14/5/1 | 0.064 |
| RANDPAUSE vs NATIVE, seeds 20-39 | 6.30 vs 2.00 | 20/0/0 | 1.9e-06 |
| RANDPAUSE vs EMPTY, seeds 20-39 | 6.30 vs 6.05 | 10/8/2 | 0.81 |

The benefit belongs to pausing itself. The terrain readout adds nothing measurable to it.

### 3c. The pause finding replicates on new seeds and without the shock
- New seeds 20-39, 4x6: EMPTY vs NATIVE +4.05 births per lineage, 18/2/0, p = 0.0004; final population 29.2 vs 23.4.
- No shock (regrowth x1.0), 4x6, seeds 0-19: EMPTY vs NATIVE +3.95, 20/0/0; final population 35.7 vs 29.8.
So it is not an artifact of the tested seeds or of the resource shock.

### 3d. Mechanism: restraint, working through the world's stock
Pausing arms harvest less (late harvest 308 vs 345 at 4x6; per-capita 0.0366 vs 0.0420) and lowest world stock is higher (0.363 vs 0.331). Commons only permits births when world stock is above a threshold. Less harvesting keeps stock up, so births keep being permitted after tick 300: NATIVE births per 100 ticks fall to 5.2, 3.1, 3.0; EMPTY holds 8.2, 10.4, 8.0.

### 3e. It is size-dependent, and "births" overstates it
- Deaths rise too: 60.3 per run vs 46.5 at 4x6. Post-shock births partly measure turnover.
- Paired final population, EMPTY minus NATIVE: +3.45 at 4x6 (13 wins, 7 losses) but -2.1 at 2x3 (4 wins, 13 losses, 3 ties).
Rest helps the crowded world and costs the sparse one.

### 3f. Inherited ground: content now varies, mass still does not
- Mass is exactly 96 in every OWN, MATCHED and FLAT birth (938 + 950 + 943 at 2x3; 1336 + 1335 + 1388 at 4x6). The ceiling still removes that axis of variation.
- Content is now distinct between parents: mean L1 distance about 90-99 of 192 even within a quadrant (first build: near zero). That fixes the birth-quadrant problem.
- Lineage signal is weak: same-lineage pairs differ by 92-96, cross-lineage by 103-109.

## 4. Receiver (code read plus demo rerun)

- Fixed from round one: journal keyed by subject; wrong parent, invented ground and real signed checkpoints at 7 and 9 all refused; concurrent pair commits once.
- Every refusal except the bad signature reduces to "differs from the enrolled digest". The receiver does not derive the ground from a parent field; the operator-side demo does, before enrollment. All claims therefore rest on operator enrollment, as the README says.
- Given enrollment pins birth, head and tape, the witness signature adds no protection in this fixture.
- One handoff per subject, permanently. A second legitimate migration is impossible until the registry grows a sequence.
- The SQLite write lock is held while Node runs (20 s timeout). A slow packet blocks every other subject.
- Missing packet fields raise KeyError, not ValueError. Still fail-closed.

## 5. Surprise ledger entry (the three questions)

Surprise: resting about half of ordinary moves raises births and, when crowded, population.
1. Replicates? Yes: 20/20 on original seeds, 18/2 on new seeds, 20/0 without shock.
2. Heritable? Not yet. It is a rule applied to every descendant, not a trait.
3. Inside the gate? Yes. It changes movement only.
Verdict: keep and watch. Do not patch.

## 6. Blue sky

1. **Make rest the first gene.** Give each newborn a pause propensity copied from its parent with a small mutation. This world already rewards it differently by density, so there is a predicted answer to falsify: crowded worlds should drift toward rest, sparse ones away. That closes the loop heredity -> behaviour -> survival for the first time.
2. **Run the cheater test.** Rest lowers the rester's own harvest and helps everyone through shared stock. A never-rest lineage should invade. Whether household structure (shared map, spacing, budding) protects rest is the first real job for the constitution. Preregister the prediction either way.
3. **Lift the 96 ceiling** so a parent with more experience can pass on more.
4. **Give the readout room.** Move the threshold, or make it relative, so check is not above it nearly all the time. Until then terrain cannot matter.
5. **Score more than births.** Add final population, lineage persistence and deaths to the primary measure.

## 7. Caveats on my own runs

Sections 3b, 3c and the new-seed part of 2 are exploratory, outside the frozen protocol, run once. RANDPAUSE averaged slightly more pauses per run than EMPTY (3,595 vs 3,278 on seeds 0-19), so "random beats terrain" is not established; "random is at least as good" is. Original traces untouched.

Files: `analyze.py`, `analyze_output.txt`, `extra.py`, `extra_output.txt`, `extra_runs.json`, `receiver_rerun/`, `live_rerun_receipts/`.
