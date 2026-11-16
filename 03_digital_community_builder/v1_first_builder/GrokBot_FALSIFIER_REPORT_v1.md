# Falsifier report: "First digital community builder handoff"

Prepared Thursday 12 Nov 2026, about 6:45 AM CST, by Grok Bot (Chief of Staff), Falsifier B (history seat). Nothing was published, pushed or sent.

Tags: **DOC** = what this pack's documents say. **OBS** = what I observed in this run. **PRIOR** = checked against earlier files already on this box.

---

## Executive summary

**What I tested**
- I scanned the pack for secrets.
- I checked integrity and ran `independent_run`.
- I rebuilt all 48 births independently.
- I ran 36 attack and rejection cases against the Node receiver, plus 8 SQLite and Gate cases.
- I wrote a second reader in exact rational arithmetic. It does not import the pack's code.
- I compared the inherited field with empty, flat and foreign fields.
- I reproduced all 12 rows of `reference.json` from the vendored sim without the capture hooks.

**What held (OBS)**
- `independent_run` reproduced every scientific output byte for byte: `summary.json`, `resumed.json`, `comparison.json`, `receiver.sqlite`, and both decompressed world archives.
- Only the material tied to the witness key changed: the witness public key, the permit signature, and the three negative-test fixtures. That is what should happen.
- World outcomes: FULL ended with 28 members and NO_ROLES ended with 0. All 12 rows of `reference.json` (4 variants × seeds 0–2) reproduce exactly from the vendored sim set to 2 lineages × 3 founders.
- Birth: parent `commons/0/0` produced child `commons/0/6` at tick 25.
  - My independent rebuild reproduces the parent field and the 96-unit ground exactly.
  - It does the same for all 48 births in the run.
  - The parent field is the snapshot at the birth tick. Fields at tick−1 and tick+1 differ for all 48 births.
- Second reader: final integer terrain matches exactly. All 566 × 3 reach/check/ratio values match Python and Node.
  - Largest absolute error: 2.2e-16.
  - Largest relative error: 4.9e-16.
  - Rows outside rel 1e-9 / abs 1e-12: 0.
- The Node receiver computes the equations itself. The packet carries no readouts.
- Every rejection the pack claims happens, with the reasons recorded below.
- SQLite refuses a second resume for the same head, including from a fresh process on a reopened journal.

**What failed or did not match**
- No scientific claim failed.

**Weaknesses in how claims are enforced (OBS; none falsifies the data)**
1. **Anyone can make a birth.** The RT birth key comes from a public string. I minted a birth naming the wrong parent, and another with an arbitrary ground. With a witness signature, Node accepted both. The README discloses the test key, but "birth binds parent identity" is only as strong as that public key.
2. **"Stale head" was tested with a garbage head.** The pack's test sets the head to the literal `"wrong"`. I used real checkpoints after 4, 7 and 9 observations, correctly signed. They were rejected only because the runner supplies the expected head. When the caller pins the packet's own head, Node accepts.
3. **Some protections live only in Python or only in signatures.**
   - The wrong-parent and duplicate-birth checks the pack counts are Python in-memory checks. A new `Gate` accepts the same birth again.
   - Node has no replay memory. Duplicate-resume protection is the SQLite primary key in the Python runner, which runs after Node.
   - Node trusts the witness for the checkpoint field and the tape contents. A re-signed tape with one event dropped, or one pressure bit flipped, is accepted.
4. **"All 566 rows differed from empty" is close to automatic.** Any non-identical ground changes every row, because nothing clamps.
   - Flat and foreign grounds also differ on 566/566 rows.
   - Changes are small: mean |Δcheck| is 0.005 against empty, max 0.056. Mean |Δreach| is 0.0008.
   - The ground never changes the child's own terrain. It changes readouts only, and nothing uses those readouts yet.

**What is still open**
- The live-decision experiment under a changed resource regime. I did **not** run it. A precise protocol is in §5.
- Ecological value.
- Off-host custody.
- I could not compare against the original RT v0.2 zip or the Digital_Life_Assembly_Review zip, because neither is on this box.

**Secret scan:** clean. No real secret was found. The only key material is the published RT test key and per-run witness public keys, both documented as fixtures. No private witness key is stored.

**Did `independent_run` reproduce the scientific claims?** Yes, every numerical and structural claim. The qualifiers are the enforcement weaknesses above.

---

## 0. Secret scan

| Item | Result |
|---|---|
| Scope | All 35 extracted files; both `.gz` archives decompressed (`V2_FULL.json`, `NO_ROLES.json`); `receiver.sqlite` dumped to SQL. The zip contains no nested zips. Raw output: `raw_secret_scan.txt` |
| Patterns | password, passwd, secret, token, api key, private, `BEGIN … KEY`, salt, username, ghp_/gho_, sk-…, AKIA…, xox[bp]-, bearer, plus every hex string of 32+ characters in the JSON evidence |
| Hits | `authority.py:16`: the RT key seed is `sha256("RT02 PUBLIC TEST FIXTURE -- NOT A SECRET OR DEPLOYMENT KEY")`. This is a deliberately public fixture key; public key `4b89c681…b9b2`. The other hits are the words `Ed25519PrivateKey` (class name only) and the word "private" in Commons PREREG prose |
| Key material in evidence | Witness **public** key `86ae8f61…d1b6` (original) and `b38e4e37…d3e3` (my run); signatures; sha256 heads. **No private witness key is written anywhere.** The SQLite file holds one row: the head and the resumed JSON |
| Withheld | Nothing. There were no real secrets |

## 1. Integrity and environment

- `sha256sum -c SHA256SUMS`: 35/35 OK. SHA256SUMS covers every file in the pack except itself. Output: `raw_sha256_check.txt`.
- The outer zip's SHA-256 is `ef9b77a4ffdbdb5957db4e937f91b1d930aceb7a13f8c65f21b70eef2ca9c222`. The attachment filename `b18a53…` is not the zip's SHA-256. It appears to be an attachment ID, not a content hash.
- The original extract under `/workspace/incoming-2026-11-12/pack/` re-verified unchanged after all work.
- Versions on the box:
  - System: Python 3.13.5, NumPy 2.5.4, cryptography 43.0.0, Node v24.22.1.
- What I installed: a uv venv at `/workspace/dc-builder-handoff-2026-11-12/venv312` with **Python 3.12.16, NumPy 2.3.5 and cryptography 50.0.0**, matching what the pack declares. Node 24.22.1 was used as found.
- Cross-check: the system stack (3.13.5 / 2.5.4 / 43.0.0) also produced byte-identical `summary.json`, `resumed.json` and `comparison.json`.
- **PRIOR:** the vendored `sim_v2.py` (`b5cbf3b5…`), `run_all.py` (`17558a86…`) and `commons_sim/sim.py` (`128682a1…`) are byte-identical to 17 earlier copies on this box, for example `/workspace/incoming-2026-10-16-bundle/batch1/8395c694/commons_v2/`.
  - No copy of RT v0.2 or of either source zip exists on this box.
  - The RT v0.1 staging copy is a different model and does not contain these equations, so it cannot serve as a source for them.

## 2. FALSIFIER step 1: `independent_run`

Command, run in the working copy `/workspace/dc-builder-handoff-2026-11-12/work`:
```
../venv312/bin/python run.py independent_run
```
- Exit code 0, about 1.5 s. Stdout is in `raw_independent_run.stdout`; stderr is empty.
- `python3 -O run.py …` refuses with "Run with verification assertions enabled", as designed.

| File | vs original | Should be |
|---|---|---|
| summary.json | identical (`542909e9…`) | invariant |
| resumed.json | identical (`a2ae2f92…`) | invariant |
| comparison.json | identical (`7eaf1b3e…`) | invariant |
| receiver.sqlite | identical (`99038e62…`) | invariant (it stores the head and result only) |
| V2_FULL / NO_ROLES .json.gz | decompressed content identical; gzip bytes differ (header timestamp) | invariant content |
| fixture_trust.json | only `witness` differs; `birth` and `expected_head` (`f393f84c…`) are the same | witness key changes |
| resume_packet.json | checkpoint, permit and observations identical; only `signature` differs | signature changes |
| tampered_tape / wrong_target / stale_head | differ (re-signed with the new key) | change |

Caveat (OBS): `summary.json` fields such as `final_field_identical`, `reference_world_outcomes_match` and the `rejected` list are literal constants. They are true only because the assertions before them passed. That is valid while assertions stay enabled, and run.py enforces that.

## 3. FALSIFIER step 2: rebuild the birth, then attack it

**Independent rebuild** (`falsifier/step2_birth.py`, output in `raw_step2_births.*`)
- I recomputed each SDKP point from the raw Commons values (observation, prior_belief, x, y) using D_TOL = 0.25, read from the vendored sim.
- I rebuilt the parent fields with my own integer write rule and projection.
- First birth: parent field matches, ground matches (`[20,0,0,0,10,0…,66 at index 20,…]`, sum 96).
- All 48 births: parent field and ground match.
- Boundary: for all 48, the field at tick−1 and at tick+1 differs from the recorded one. Every parent keeps observing after the birth.
- In the sim, a tick's observations come before its births (sim_v2.py lines 88–175). So "tick ≤ birth tick" is the correct boundary.
- The child's first observation is at tick 26, one tick after birth.

**Node receiver and runner rejections** (`falsifier/step2_rejects.py`, `step2_sqlite.py`; output in `raw_step2_rejects.*`, `raw_step2_sqlite_gate.txt`)

| Case | Result | Exact reason |
|---|---|---|
| Original packet, original pins | accepted | — |
| Pack fixture tampered_tape / wrong_target / stale_head | rejected | `Error: resume binding` (same message for all three) |
| Wrong witness pin | rejected | `Error: witness signature` |
| Wrong birth-authority pin | rejected | `Error: birth binding` |
| Correctly signed checkpoint after 4 / 7 / 9 obs, runner pins the 8-obs head | rejected | `Error: resume binding` |
| Same, caller pins that packet's own head | **accepted** | Node trusts the head pin it is given |
| checkpoint.parent changed, witness re-signed | rejected | `Error: birth binding` |
| Proposal and checkpoint parent changed, birth not re-signed | rejected | `Error: birth binding` |
| Wrong parent (`commons/0/3`), birth **re-signed with the public RT test key** | **accepted** | — |
| Arbitrary ground (all 96 units in one pressure cell), public test key | **accepted**; 566/566 readout rows differ from the genuine run | — |
| Genuine different parent (0/5→0/7, 0/3→0/9), pinned to the first child's head | rejected | `Error: resume binding` |
| Same, pinned to its own head | accepted (correct: it is a valid packet) | — |
| Tape: last event dropped, permit re-signed | **accepted** | the witness can authorize a shorter tape |
| Tape: two events swapped / duplicate event / foreign subject / bin = 4 / id ≤ checkpoint.last (each re-signed) | rejected | `Error: observation continuity` |
| Tape: one pressure bit flipped, re-signed | **accepted** | Node cannot see the source |
| Point altered, not re-signed | rejected | `Error: resume binding` |
| Checkpoint field cell edited, re-signed, self-pinned | **accepted** | Node does not recompute the 8-obs prefix |
| Same edit, runner pin = true head | rejected | `Error: resume binding` |
| `field.frozen = true` | rejected | `Error: birth binding` |
| Target `node:terrain-v2` (validly signed) | rejected | `Error: resume binding` |
| Permit kind ≠ resume | rejected | `Error: resume binding` |
| Node alone, same packet twice | accepted both times | no replay state in Node |
| SQLite: duplicate resume on the reopened `independent_run` journal, fresh process | rejected | `ValueError('resume already committed')` |
| SQLite: fresh journal, first resume accepted, second rejected | rejected | `ValueError('resume already committed')` |
| Python Gate: duplicate birth | rejected | `ValueError('unregistered or replayed birth')` |
| New Gate instance, same birth | **accepted** | the Gate is in memory only |
| `Verifier.birth_matches` with parent `wrong-parent`, `commons/0/3` or `commons/0/5` | False | — |

**Reading (OBS):**
- Every rejection the pack claims is real.
- But "wrong parent" and "duplicate birth" are tested only in Python, inside the builder's own process.
- The pack's "stale head" test is a garbage string, not a real earlier checkpoint.
- Node relies on three things: the caller's head pin, the witness signature, and a public birth key. In this fixture all three are controlled by the same runner. The README says so, but the reject list on its own reads stronger than that.

## 4. FALSIFIER step 3: an independent second reader

- `falsifier/second_reader.py` is typed from the equation text in `vendor/rt/terrain.py` and `model.py`; it does not import them.
- It uses exact `Fraction` arithmetic over all 256 cells.
- It starts at birth (empty terrain plus the signed ground) and replays all 574 observations.
- Points are recomputed from the raw Commons values; 0 of 574 differed from the recorded tape.

| Check | Result |
|---|---|
| Final integer terrain vs original `resumed.json` and vs `independent_run` | identical |
| Rows compared vs Python / Node | 566 / 566; id mismatches 0 |
| Max absolute error vs exact (Python and Node) | 2.216e-16 |
| Max relative error vs exact | 4.90e-16 |
| Values outside rel 1e-9 / abs 1e-12 | 0 of 1698 (Python), 0 of 1698 (Node) |
| Equal to the correctly rounded exact value | 1007/1698 Python, 1008/1698 Node; the rest are 1 ulp off |
| Python vs Node | 30 rows not bit-identical; max difference 1.11e-16 (summation order) |
| Ranges | ratio 0.256–0.710, check 0.292–0.633, reach 0.931–0.985; no clamping anywhere |

Disclosure: the "original RT equations" I used are the vendored v0.2 files. The original zip (`06366bfd…`) is not on this box, so I could not confirm the vendoring against it.

## 5. FALSIFIER step 4: inheritance controls (honest scope)

Same tape, exact reader (`falsifier/step4_controls.py`, `raw_step4_controls.*`):
- My exact empty-ground run equals the pack's `comparison.json` `empty_ground` within tolerance.
- **Flat** = the RT v0.2 FLAT_J rule applied to the inherited ground.
- **Foreign lineage** = the signed ground of 0/5→0/7 (lineage 1, tick 25).
- **Foreign parent, same lineage** = 0/30→0/40 (tick 450).

| Control | Rows changed | mean / max \|Δratio\| | mean / max \|Δcheck\| | mean / max \|Δreach\| | first-50 vs last-50 mean \|Δratio\| | child terrain changed? |
|---|---|---|---|---|---|---|
| empty | 566/566 | 0.0065 / 0.0743 | 0.0049 / 0.0557 | 0.00078 / 0.0089 | 0.0135 → 0.0078 | no |
| flat | 566/566 | 0.0073 / 0.0692 | 0.0055 / 0.0519 | 0.00088 / 0.0083 | 0.0165 → 0.0062 | no |
| foreign lineage | 566/566 | 0.0118 / 0.1244 | 0.0088 / 0.0933 | 0.0014 / 0.0149 | 0.0365 → 0.0057 | no |
| foreign parent, same lineage | 566/566 | 0.0016 / 0.0209 | 0.0012 / 0.0157 | 0.0002 / 0.0025 | 0.0014 → 0.0025 | no |

Reading (OBS):
- Every control changes every row. So "566 of 566 differ from empty" only shows that the ground enters the readout, which follows directly from the equation.
- The rows-changed count cannot tell lineage-specific information apart from mere presence of mass.
- The parent's actual field is distinguishable from flat or foreign fields only by small magnitudes.
- Inherited vs empty: ratio is higher on 562/566 rows, since the ground adds mass to the pressure channel.
- The ground never alters the child's own terrain. Its only effect is on readouts that nothing consumes yet.

**Live decisions under a changed resource regime: NOT RUN.** The pack specifies no decision rule. Running one would mean inventing the coupling. Here is the recommended protocol, to be frozen (with SHA-256) before any run:
- **Arms:** native Commons v2 (no adapter); INHERITED; EMPTY; FLAT (the FLAT_J rule); FOREIGN (ground from a parent of the other lineage, as in the RT FOREIGN_J rule). Every newborn, not only the first, receives its arm's ground at birth and reads after each observation.
- **Decision rule (one rule, fixed in advance; the Designer/Rusty should approve it):** at the move step, an agent with `check ≥ 0.5` stays put and re-observes for one tick instead of moving. Otherwise the native rule applies. No other behaviour changes.
- **Resource change:** at t = 300, multiply the vendored REGROW constant by 0.7 for the rest of the run. As a secondary regime, redraw patch centres at t = 300 from a separate RNG stream so native draws are untouched.
- **Seeds:** 0–19 (the 20-seed convention in commons_v2 PREREG), with 2×3 founders. Repeat at the native 4×6.
- **Primary outcome:** extinction by t = 600 (yes/no), paired by seed: INHERITED vs each control.
- **Secondary outcomes:** pop_final, harvest_late, per_capita, families_alive.
- **Record for every seed and arm:** the full birth/death/lineage history and the per-tick population, including extinctions. A null result is a valid outcome.
- Report all seeds. No claim of ecological value unless the primary outcome differs and the frozen threshold is met.

## 6. Additional scrutiny

1. **Ways the match is circular (OBS).**
   - Python and Node are two ports by the same author of the same equations. Their agreement shows the port is faithful, not that the science is right.
   - The world-outcome "match" compares the vendored sim with numbers in `reference.json` produced by the same code. I reproduced all 12 rows without the hooks, which shows the hooks don't perturb the RNG.
   - I found no earlier copy of those six-member numbers on this box (a search for 509.4563 found nothing). So "matches the earlier archive" is **DOC only**; I could not confirm it against prior files.
2. **Confusing labels in reference.json (OBS).**
   - It labels `reference_fixture` as 4 households × 6 founders, while every run in it has `initial_members: 6` (2 × 3).
   - The pack's check compares only the keys the sim returns. `initial_members` and `subsequent_births` are never checked. Subsequent births do agree with the archives: 48 for FULL, 5 for NO_ROLES.
3. **Problems with the adapter mapping (OBS; the README already calls it experimental).**
   - The size axis is always 1, so 3 of 4 axes carry information.
   - The pressure bit is fully redundant with kinetics bin ≥ 1 (0 of 10,222 rows disagree).
   - 4,087 of 10,222 noisy observations are negative and clamp to density bin 0.
   - Position is a quadrant code (2·[x≥16] + [y≥16]) but is treated as an ordinal distance in both the kernel and the slice window. Quadrants 1 and 2, which are diagonal, count as distance 1. Quadrants 0 and 2, which are side by side, count as distance 4 (weight factor 3·2²). This affects which parent cells are inherited and how much they weigh.
   - The child's slice point uses density 0 and kinetics 0 by fiat.
4. **Node implements the equations (OBS).** It does not trust precomputed readouts. It hard-codes reach baseline 0.9 after checking `reach_basis_points === 9000`, and closure = 0.
5. **SQLite (OBS).** Uniqueness is the `head TEXT PRIMARY KEY`. That gives one result per checkpoint head as claimed, and it holds across a reopen.
6. **History-seat disclosure.**
   - The parent has published commons-dwelling-grace and relational-transitions-v0.1, and ran triad rounds 1–4.
   - From that history I used only (a) byte comparisons against earlier Commons source copies on this box (PRIOR, above) and (b) a read-only look at the RT v0.1 staging folder, which does not contain these equations.
   - No earlier review was used to close any finding here.
   - I read the pack's README and FALSIFIER.md before testing, so I was not blind to the claims.
   - Round 5 material was not touched.

## Commands

```
cd /workspace/dc-builder-handoff-2026-11-12
cp -a /workspace/incoming-2026-11-12/pack work && (cd work && sha256sum -c SHA256SUMS)
uv venv -p 3.12 venv312 && VIRTUAL_ENV=venv312 uv pip install numpy==2.3.5 cryptography==50.0.0
cd work && ../venv312/bin/python run.py independent_run
cd ../falsifier && ../venv312/bin/python step2_birth.py && ../venv312/bin/python step2_rejects.py \
  && ../venv312/bin/python step2_sqlite.py && ../venv312/bin/python step3_compare.py \
  && ../venv312/bin/python step4_controls.py && ../venv312/bin/python step6_reference.py
```
Raw outputs are in `/workspace/dc-builder-handoff-2026-11-12/`: `raw_*.txt|json`, `work/independent_run/`, `reject_tests/` (every attack packet), `scan/` (the decompressed archives and the SQLite dump).
