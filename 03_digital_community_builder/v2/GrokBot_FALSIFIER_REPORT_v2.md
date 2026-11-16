# Falsifier report: Digital Community Builder v2

Prepared by Grok Bot (Falsifier B, history seat) on 2026-11-12, between 06:58 and about 07:40 AM CST.
Nothing was published, sent or pushed. Round 5 material was not touched.

**Blindness disclosure.** This was not a blind check. The parent and I read README.md, FALSIFIER.md and protocol.json before testing. I also reviewed the v1 pack this morning and have history with the published commons-dwelling-grace and relational-transitions-v0.1 work. I did not use earlier reviews to close any v2 finding. Every v2 conclusion below rests on tests run today against this pack.

**Tags.** DOC means a claim stated in the pack's documents. PRIOR means a finding from an earlier round, here this morning's v1 review. OBS means something I measured myself today.

---

## 1. Executive summary

**What I tested.** I tested the whole v2 pack, outer SHA-256 `7ae94f6d…53d7`, with 284 files. The work had seven parts:

- a secret scan;
- manifest and protocol checks;
- the complete 240-run live schedule, rerun twice;
- a byte-for-byte comparison of every trace and both receipts;
- my own genealogy, statistics, donor and mass audit, written without the pack's verifier;
- an instrumented, passive rerun to trace move precedence and readout sensitivity;
- a receiver attack battery that goes beyond the pack's demo, plus Node-alone tests.

**What held (OBS):**

- **Integrity.** SHA256SUMS lists 283 entries and covers every file except itself. All 283 match. `protocol.sha256` matches `protocol.json`: `ba0482af64463a6e29fcc296b2238086b00605fa0303ae508d721cc57098a53e`.
- **Full rerun.** `OPENBLAS_NUM_THREADS=1 python live.py new_live --workers 4` took 63.5 s wall time. All 240 traces matched the pack byte for byte, including the gzip containers. So did `runs.json` (`4b83e773…f417e`) and `summary.json` (`ebb1aedc…a9ab`). A second rerun with `--workers 1` (4 min 20 s) also matched byte for byte. `verify_live.py evidence/live` passed, as did `verify_live.py evidence/live --repeat new_live`. Its output is identical to the pack's `evidence/verification.txt`.
- **Native references.** All 12 unshocked native references (2 lineages × 3 founders) reproduce from the *unpatched* vendored `sim_v2.py`, without using `live.py`. The instrumented loader, with no shock and no pause, also reproduces 20 of 20 archived 4×6 V2_FULL per-seed outcomes in the vendored `commons_v2/results.json`.
- **Genealogy.** My own audit of all 240 runs found 0 problems. It checked:
  - census against births and deaths every tick;
  - that every parent was alive and of the same lineage;
  - contiguous IDs;
  - births only on the 25-tick schedule, with at most one birth per parent per tick;
  - receipt totals, peak and final population, and late harvest;
  - pause invariants.
- **README table.** Every mean matches exactly. The fractions are:
  - 2×3: 243/20, 51/4, 527/40, 517/40, 101/8 and 497/40;
  - 4×6: 227/80, 263/40, 55/8, 619/80, 531/80 and 309/40.
- **Primary contrast.** I recomputed OWN − MATCHED myself with an exact sign test:
  - 2×3: −0.425 per lineage (−17/40), 8 wins, 10 losses, 2 ties, p = 53381/65536 = 0.8145;
  - 4×6: −0.300 per lineage (−3/10), 8 wins, 9 losses, 3 ties, p = 1.
  Neither size meets the frozen criterion (≥ 1 birth per lineage and p ≤ 0.05 at both sizes). **The primary result is null, as the pack says.**
- **Donor coverage.** 907/950 at 2×3 (713 cross-lineage, 194 same-lineage, 43 fallbacks) and 1334/1335 at 4×6 (1325 cross, 9 same, 1 fallback). I recomputed every donor choice independently, with my own hash and largest-remainder code: 0 mismatches. Every fallback was a quadrant where the parent was the only living member. Channel mass is conserved in every MATCHED and FLAT birth.
- **No extinction.** No run ended extinct. The smallest final population was 15.
- **Empty against native.** I recomputed this pairing:
  - 4×6: +3.800 per lineage, 20 wins, 0 losses, 0 ties, p = 2⁻¹⁹ ≈ 1.91×10⁻⁶;
  - 2×3: +0.475, 9 wins, 8 losses, 3 ties, p = 1.
- **Pause rule.** It is implemented as written. Pauses happen only on ordinary displacing moves by descendants with check ≥ 0.5, never on two ticks in a row. A pause runs after the native move has drawn all its random numbers and changes position only. In all 240 runs, the recorded pauses equal exactly the set of eligible decisions with high check that were not blocked by the previous tick.
- **No-pause diagnostic** (not scored). With the threshold made unreachable, 200 of 200 pause-arm runs equal the packaged NATIVE run exactly. NATIVE is therefore the exact no-pause counterfactual: the pause is the only path by which terrain touches the world.
- **Receiver.** Every documented refusal reproduces with a fresh registry, before the genuine checkpoint is consumed. So do four extra signed attacks and two foreign-key attacks. In 10 of 10 trials of 8 concurrent OS processes, exactly one commit went through. A fresh process refuses the subject after commit, and re-enrolling it fails. The committed output matches the Python replay through 566 observations. `receiver_demo.py new_receiver` gives a `summary.json` byte-identical to the pack's.
- **Secret scan.** Clean (Section 2).

**What did not match, or needs qualifying (OBS):**

1. **The inherited ground barely moves the decision.** In every pause arm, check is already ≥ 0.5 on 75–81% of eligible descendant moves, *including EMPTY (76.2% at 2×3, 75.3% at 4×6)*. That comes from the personal field's pressure channel. Zeroing the inherited ground would flip only 1.1–1.4% of decisions in OWN and MATCHED, 0.7% in FLAT and 3.3–3.5% in LEGACY. All OWN, MATCHED and FLAT grounds hit the 96-unit ceiling (938 of 938, 950 of 950, …). MATCHED and FLAT also keep OWN's per-channel totals, so the primary contrast only tests how 96 units are *arranged* across 16 bins. The null primary is therefore a low-power test of a weak lever. It is not evidence that parent-specific terrain "doesn't matter" in general.
2. **Trajectories split early.** OWN and MATCHED first differ in a pause between ticks 26 and 78 of 600 (median 37 at 2×3 and 30.5 at 4×6), long before the tick-300 shock. After that the populations differ. Pairing by seed controls only the initial world, not per-agent histories. The post-shock difference is effectively two chaotic draws per seed.
3. **The highlighted EMPTY > NATIVE pattern is post hoc.** The protocol's secondary list is "OWN against other arms, …". It does not pre-specify EMPTY against NATIVE. The pre-specified secondary OWN − NATIVE is +3.74 per lineage at 4×6 (18 wins, 2 losses, p = 4.0×10⁻⁴) and +0.60 at 2×3 (p = 1). Every pause arm beats NATIVE at 4×6: FLAT 20/0, LEGACY 19/1, MATCHED 18/0/2, OWN 18/2, EMPTY 20/0. So this is a pause-rule effect, not an inheritance effect.
4. **More births come with less late harvest.** The README doesn't say this. The same pause arms that raise births *lower* late harvest at both sizes:
   - EMPTY − NATIVE: −65.6 at 2×3 (1 win, 19 losses) and −37.4 at 4×6 (1 win, 19 losses);
   - OWN − NATIVE: 0 wins, 20 losses at 2×3.
   At 2×3, EMPTY also ends with a smaller final population than NATIVE (4 wins, 13 losses, 3 ties, nominal p = 0.049, uncorrected). Late harvest and final population are pre-specified secondaries. "Births up" is not the same as "doing better".
5. **Pause rates are almost constant** across pause arms: 43–47% of eligible moves. The ceiling is about 50% because of the alternate-tick rule. The pause behaves close to "descendants move about every other tick", whatever ground they carry. That is a hypothesis to test; I have not shown it.

**Enforcement (OBS).** With `receiver.py` and its operator-enrolled SQLite registry, all wrong-parent, invented-ground, stale-checkpoint, edited-checkpoint and altered-tape attacks are refused, even when an attacker holds the legitimate birth and witness keys. These protections rest *entirely* on the registry:

- someone with write access who enrolls a forged record gets it accepted, even with their own keys;
- resetting `result` to NULL, or deleting and re-enrolling the row, lets the same packet be accepted again;
- `register()` validates nothing.

**Node alone** still accepts a wrong parent, invented ground, real earlier checkpoints and edited checkpoints when the caller pins the packet's own head. It accepts every re-signed tape change (shorter, longer, missing first event, flipped pressure) under *any* head pin, because Node does not pin the tape.

**This morning's four v1 weaknesses:**

| v1 weakness | Status | Why |
|---|---|---|
| 1. Public RT test key could mint births | Narrowed. Closed in the receiver path if enrollment is trusted. | Fresh ephemeral keys; the RT02 public key isn't enrolled and is refused; signed wrong-parent and invented-ground births are refused by the registry pin. Node alone still accepts any birth signed by whatever key the caller passes. |
| 2. Stale head only tested with "wrong" | Closed in the receiver path if enrollment is trusted. | Real signed checkpoints at 7, 9, 10 and 573 refused. Node alone with the packet's own head still accepts them, as in v1. |
| 3. Gates only in Python memory, or SQLite after Node; Node accepted altered tapes | Closed for one handoff per subject in the receiver path if the registry is trusted and intact. Still open for Node alone. | The SQLite check now runs *before* Node, inside BEGIN IMMEDIATE; it survives a fresh process and concurrency. Node alone still accepts re-signed tape edits. |
| 4. "566 rows differed" was close to automatic; ecological value unmeasured; live experiment not run | Addressed in design, but the result is null and the lever is weak. | A live experiment was run with MATCHED/FLAT/EMPTY controls. Primary is null. The ground changes about 1% of decisions. The striking 4×6 effect belongs to the pause rule, not inheritance. Harvest falls. |

**Still open:**

- the protocol freeze order cannot be proven;
- the original source zips are not on this box, so the RT modules cannot be compared against independent originals;
- seeds 0–19 are known seeds, not a holdout;
- the positional kernel treats quadrant IDs as ordinal;
- successive legitimate migrations are impossible by design (one handoff per subject, ever);
- registry and operator custody are trusted;
- there is no rate-matched random-pause control, so the readout's information content is untested.

---

## 2. Secret scan (OBS)

**Scope.** I scanned every file in the extracted pack: 284 files, which became 526 objects after decompressing all 240 `.gz` traces and the fixture `.gz`, and dumping `receiver.sqlite` to SQL. I also scanned the raw SQLite bytes, including free pages. The pack has no nested zips. There is no SQLite `-journal` or `-wal` file; the only journal is `receiver.sqlite` itself.

**Patterns.** PEM and OpenSSH private keys, AWS keys, GitHub and Slack tokens, JWTs, api_key/secret/token/bearer assignments, password and username assignments, "salt", secret-related words, and 64-hex, 128-hex and long base64 strings.

**Findings:**

- No passwords, usernames, tokens, salts or PEM or SSH keys.
- 64-hex strings are SHA-256 digests or Ed25519 *public* keys. In the traces, all 240 hits are the protocol hash.
- 128-hex strings are Ed25519 *signatures*, which are public.
- **No private signing keys are stored.** I treated every 64-hex string in `evidence/receiver/` and the SQLite dump (301 candidates) as a possible Ed25519 seed. None derives either enrolled public key (witness `8e2ccbf9…`, birth `c1049670…`). That supports the claim that private keys are ephemeral.
- `vendor/rt/authority.py` contains the **published RT02 public test fixture** key derivation, `sha256("RT02 PUBLIC TEST FIXTURE -- NOT A SECRET OR DEPLOYMENT KEY")`. It is intentionally public, as in v1, and not a secret. It is not enrolled in the v2 registry.
- My own audit outputs hold public keys only. I checked that none of my ephemeral private-key hex appears in any output file.

Nothing was withheld, because no real secret was found.

## 3. Integrity, freeze and versions

- `sha256sum -c SHA256SUMS`: 283/283 OK. The only file not listed is SHA256SUMS itself. That is normal, but it means the manifest is only as trustworthy as the outer zip hash. (OBS)
- `sha256(protocol.json)` = `ba0482af…a53e` = `protocol.sha256`. Every trace embeds the same `protocol_sha256`, and `live.py` refuses to run if the two disagree. (OBS)
- **Freeze order cannot be proven.** A hash proves which protocol the runs used, not when it was written. Zip entry times (author-local, no zone):
  - `protocol.json`, `protocol.sha256` and `live.py`: 2026-11-12 06:47:22;
  - traces: 06:47:28 to 06:48:28;
  - `runs.json`: 06:48:28;
  - SHA256SUMS: 06:51:36.

  The final protocol file was saved 6 s before the scored traces were written, which fits a run of about 60 s. That is consistent with freezing first. It cannot exclude earlier, unrecorded runs under other protocol drafts. There is no external timestamp, such as a commit or post, from before scoring. (DOC/OBS)
- **Versions used:**
  - Python 3.12.16 (venv `/workspace/dc-builder-handoff-2026-11-12/venv312`);
  - NumPy 2.3.5;
  - cryptography 50.0.0;
  - Node v24.22.1;
  - SQLite 3.53.1;
  - Linux 6.12 x86_64, 8 CPUs.
  System Python 3.13.5 was not used.
- **Vendored sources:**
  - All 12 vendored Commons files are byte-identical to independent earlier copies on this box (`/workspace/incoming-2026-10-16-bundle/batch1/8395c694/…`, `/workspace/the-terrain-remembers/00_commons_swarm/…`). Those predate both packs.
  - The 3 RT modules (`authority.py`, `model.py`, `terrain.py`) match only the v1 pack copies from this morning, which is not independent.
  - The relational-transitions **v0.1** `model.py` on this box differs, as expected for a different version.
  - Neither `Digital_Life_Assembly_Review.zip` (`a1de2370…`) nor `Relational_Transitions_v0_2_2026-11-10.zip` (`06366bfd…`) is on the box. **That is a provenance gap, not a pack failure.**
  - `fixtures/commons_seed0.json.gz` decompresses to `a89a90c6…c027`, the same as the v1 pack's `evidence/V2_FULL.json.gz`. `fixtures/reference.json` is identical to the v1 pack's `reference.json`.

## 4. Step 1: replay, references and genealogy

**Commands** (CST; cwd `/workspace/dc-builder-v2-2026-11-12/run`, a copy of the clean pack):

```
OPENBLAS_NUM_THREADS=1 venv312/bin/python live.py new_live --workers 4      # 06:58:53–06:59:56, real 63.5 s, user 4m10s
OPENBLAS_NUM_THREADS=1 venv312/bin/python live.py new_live_w1 --workers 1   # real 4m20s
OPENBLAS_NUM_THREADS=1 venv312/bin/python verify_live.py evidence/live                     # pass, 19.9 s
OPENBLAS_NUM_THREADS=1 venv312/bin/python verify_live.py evidence/live --repeat new_live   # pass, 18.1 s
```

- Both reruns: 240/240 traces identical after decompression and as gzip bytes; `runs.json` and `summary.json` identical. (OBS)
- References: 12/12 reproduced from the unpatched `sim_v2.py` with FAMS = 2 and FOUNDERS = 3: V2_FULL, V2_LONE, NO_ROLES and V2_SELF_REPLICATING, seeds 0–2 each. A minor note: the pack's verifier and my check both compare the keys `run()` returns, so the fixture's `initial_members` and `subsequent_births` fields are not checked. 20/20 archived 4×6 V2_FULL seeds also reproduce through the patched loader. (OBS)
- My genealogy audit (`audit/audit_traces.py`, independent of `live.py` and `verify_live.py`): 0 problems across 240 runs. (OBS)

**Post-shock births per founding lineage, recomputed from the birth records (all match README):**

| Arm | 2×3 | 4×6 |
|---|---:|---:|
| NATIVE | 12.150 | 2.8375 |
| OWN | 12.750 | 6.5750 |
| MATCHED | 13.175 | 6.8750 |
| FLAT | 12.925 | 7.7375 |
| EMPTY | 12.625 | 6.6375 |
| LEGACY | 12.425 | 7.7250 |

**Other per-arm figures (OBS).** Mean late harvest: 2×3 NATIVE 275.9 against 203–212 in pause arms; 4×6 NATIVE 345.4 against 306–313. Total births at 4×6: NATIVE 965 against 1309–1397. Pauses: 45k–49k at 2×3 and 66k–68k at 4×6. Rate of pauses among eligible moves: 0.43–0.47. Extinct runs: 0 in every arm. Minimum final population: 15 (2×3 MATCHED and LEGACY).

## 5. Step 2: move precedence and draws

I used an instrumented copy (`run/instr_live.py`, built by `audit/make_instr.py`). It only logs. Its 240 traces and both receipts are byte-identical to the pack's, so the logging changed nothing. (OBS)

**Categories of descendant moves, all seeds, pause arms:**

| Category | 2×3 | 4×6 | Paused |
|---|---:|---:|---|
| active target | 3,941 | 5,713 | never |
| new target | 563 | 750 | never |
| dwell | 143,336 | 188,117 | never |
| no-op | 21,632 (1,863 used RNG draws) | 29,082 (2,901 used RNG draws) | never |
| ordinary (eligible) | 525,773 | 770,975 | when rule applies |

Founders are never paused.

**Rule check.** Across all 240 runs, the set of recorded pauses equals exactly {eligible ordinary moves with check ≥ 0.5 and no pause at t−1}. There are 0 exceptions. Examples, all 2×3 seed 0:

- **Active target is not paused.** OWN, agent 11, ticks 77–79: [19,5]→[19,4]→[19,3]→[19,2], toward target [19,29]. EMPTY, agent 11, tick 77: [15,27]→[16,28], target [26,4].
- **New target is not paused.** OWN, agent 11, tick 76: [20,6]→[19,5], target newly set to [19,29]. MATCHED, agent 13, tick 101: a call target was selected at the agent's own cell [1,28], so no step. At tick 102 the target was reached and cleared, and a new target [14,23] was chosen.
- **Dwell is not paused.** OWN, agent 6, ticks 40–41 at [0,5], including check 0.519 at tick 41: dwelling, so not eligible.
- **No-op is not paused.** OWN, agent 7, ticks 45–46 at [28,4], with check 0.517 and 0.535.
- **Two consecutive eligible ticks.** OWN, agent 6: eligible at ticks 31 and 32 with check ≥ 0.5. It paused at 31 and was blocked and moved at 32. Same pattern at ticks 33/34 (agent 6), 34/35 (agent 7) and 36/37 (agent 7). Across all pause arms, 34k–52k high-check decisions per arm and size were blocked this way.

**Draws.** The wrapper runs the entire native move, including all `arng` draws (scout noise, random-walk integers), before it reverts the position. No draw happens between the native move and the revert. The instrumentation recorded the RNG state before and after every native move: draws are consumed whether or not a pause follows. A pause sets `x, y` back and nothing else. `a.run` was already reset to 0 by the native non-dwelling path; `d`, belief and target are untouched. A paused agent is not counted as "stuck" and does not become a grace candidate. (OBS)

**After divergence.** OWN and MATCHED first differ in pauses at ticks 26–78 (2×3, median 37) and 26–55 (4×6, median 30.5). Population or harvest diverges 1–6 ticks later. EMPTY and NATIVE first differ at ticks 32–58. After that, the arms have different agents, births, RNG consumption and positions. Later comparisons are between different histories, not between matched agents. The protocol scope acknowledges this. (OBS; DOC)

**Fairness of NATIVE against pause arms.** NATIVE skips the field entirely. Field writes have no world side effects. The no-pause diagnostic proves this: 200/200 pause-arm runs with an unreachable threshold reproduce NATIVE exactly. The comparison is fair as "pause rule on vs off". It is *not* a test of the readout's information, because no control pauses at the same rate at random. Founders never pause in any arm. LEGACY's parent field uses a different pressure rule, but its live reader and movement are the same. (OBS)

## 6. Step 3: donors, mass and interpretation

- **Donor choice.** For all 2,285 MATCHED births, I recomputed the candidate set from instrumented positions: living members in the child's quadrant at the end of the move phase, minus the parent, preferring other lineages. I recomputed the minimum of `sha256(canon([seed, child, donor]))` with my own code. 0 mismatches. Candidate quadrants are all correct. (OBS)
- **Fallbacks.** 43 at 2×3 and 1 at 4×6. In every one, the parent was the only living member of the quadrant. Ground equals OWN in all of them. Examples: 2×3 seed 0, tick 50, child 9, parent 3 alone in quadrant 3. 4×6 seed 0, tick 575, child 81, parent 0 alone in quadrant 3. (OBS)
- **Same-lineage donors.** 194 at 2×3 and 9 at 4×6, all chosen because no other lineage was in the quadrant. Examples: 2×3 seed 0, tick 25, child 6, parent 0, donor 1 (both lineage 0). 4×6 seed 2, tick 550, child 105, parent 21, donor 18 (candidates 18, 27 and 100, all lineage 3). (OBS)
- **Donors that had not reproduced.** 649/907 donors at 2×3 and 950/1334 at 4×6 had not reproduced by that tick; 585 and 822 never reproduced in the run. Founders were donors 261 and 682 times. In 118 and 187 cases, the donor reproduced on the same tick. This is allowed by the protocol (DOC), but MATCHED is "another living member's terrain", not "another parent's terrain". (OBS)
- **Mass conservation.** Per-channel totals are identical to OWN in every MATCHED birth (2,285) and FLAT birth (2,331). No zero donor or OWN channels occurred, so the flat-channel path was never exercised. The OWN projection hit the 96 ceiling in 100% of births. OWN, MATCHED and FLAT grounds always total exactly 96, with about 59% in the pressure channel. LEGACY totals range from 0 to 96. (OBS)
- **Interpretation.** Because channel totals are matched and fixed at 96, OWN − MATCHED tests only *where* 96 units sit across 16 position-by-kinetics bins. Zeroing the ground flips only about 1.1–1.4% of eligible decisions. Then trajectories diverge chaotically within a few ticks of the first flip. A null here is weak evidence about parent-specific terrain. (OBS)
- **Seeds.** Seeds 0–19 were used in earlier Commons and replay work. The protocol itself says this is "a prospective live run on known seeds, not a blind or holdout result" (DOC). These results hold for these seeds; no new-seed replication exists.

## 7. Step 4: receiver

**Fresh registry; each attack in a fresh OS process; before the genuine checkpoint is consumed (OBS).** Each attack below was signed with the legitimate keys unless noted. The registry stayed uncommitted after each refusal.

| Attack | Refusal |
|---|---|
| wrong parent (commons/0/5) | `birth conflicts with trusted source record` |
| invented ground | `birth conflicts with trusted source record` |
| real signed checkpoints at 7, 9, 10 and 573 | `checkpoint conflicts with trusted source record` |
| re-signed checkpoint edit | `checkpoint conflicts with trusted source record` |
| birth re-signed with the public RT02 key | `checkpoint conflicts with trusted source record` |
| birth re-signed with an attacker key | `checkpoint conflicts with trusted source record` |
| re-signed tape: shorter, extended, missing first event, flipped pressure | `observations conflict with trusted source record` |
| bad witness signature | Node `Error: witness signature`, surfacing in `receiver.py` as `CalledProcessError` |
| genuine content signed by an attacker witness key | Node `Error: witness signature`, as above |
| permit subject swapped | `unknown subject` |

The CLI does not show Node's reason; only the demo inspects stderr. (OBS)

- **Concurrency.** 10 trials of 8 simultaneous `receiver.py` processes on a fresh registry: each time exactly 1 accepted and 7 refused with `handoff already committed for subject`. The committed result matches the Python replay: field exact, 566 metrics within 1e-12. (OBS)
- **After commit, fresh processes.** The genuine replay and every attack above are refused with `handoff already committed for subject`; subject swap still gives `unknown subject`. After commit, refusals are generic: content is not re-examined. Re-enrolling gives `sqlite3.IntegrityError: UNIQUE constraint failed: handoffs.subject`. (OBS)
- **A second, legitimate later checkpoint** (obs 100) after commit is refused. Before commit, a different valid checkpoint is refused as a conflict. **Successive legitimate migrations are impossible** in this design: one result per subject, ever. The README lists this as open. (DOC/OBS)
- **`receiver_demo.py new_receiver`** ran in 0.8 s and gave a `summary.json` byte-identical to the pack's. Packet content is identical apart from fresh keys and signatures. That includes the proposal, observations and checkpoint field. The checkpoint head digest differs because it covers the birth signature. The stored results (field and metrics) are identical. The pack's packet signatures verify against the public keys enrolled in the pack's SQLite, and all three registry pins match the pack's packet. (OBS)

**What depends on operator enrollment and registry custody (OBS):**

- `register()` checks nothing. It stored a malformed record with non-hex keys. Enrolling the wrong-parent record with legitimate keys led to it being **ACCEPTED**. Enrolling a wrong-parent, invented-ground, truncated-tape record with *attacker-held* keys also led to it being **ACCEPTED**. The only safeguard is the docstring "Call with independently reconstructed source state", together with the demo's rebuild from the hash-pinned seed-0 trace.
- Setting `result = NULL` after commit led to the genuine replay being **ACCEPTED** again. So did deleting the row and re-enrolling. Replay protection relies on registry integrity.
- So every v1-closing claim holds *only* under "operator enrollment is honest and the SQLite file is not writable by an adversary". The README states this assumption (DOC). The tests confirm it is load-bearing.

**Node alone (`resume.mjs`, legitimate public keys passed by the caller) (OBS):**

| Packet | Pin = packet's own head | Pin = genuine head |
|---|---|---|
| genuine | accepted | accepted |
| wrong parent, invented ground | **accepted** | rejected (`resume binding`) |
| real checkpoints at 7, 9, 10 and 573; checkpoint edit | **accepted** | rejected (`resume binding`) |
| re-signed tape: shorter, extended, missing first event, flipped pressure | **accepted** | **accepted** |
| bad or foreign witness signature | rejected (`witness signature`) | rejected |
| birth signed by RT02 or attacker key | rejected (`birth binding`) | rejected (`resume binding`) |

Node pins nothing about the tape beyond the witness signature. It trusts whatever keys and head its caller supplies. The README's statement that "the standalone Node reader is a numerical component" is accurate.

## 8. Step 5: EMPTY against NATIVE (recomputed; no new experiment run)

**Post-shock births per lineage, EMPTY − NATIVE:**

- 2×3: +0.475 (19/40); 9 wins, 8 losses, 3 ties; p = 1. Deltas: [6, 15, 2, −1, 8, 2, 0, 6, −5, −3, 4, 0, 0, −4, −2, 2, 13, −2, −9, −13].
- 4×6: +3.800 (19/5); 20 wins, 0 losses; p = 1/524288 ≈ 1.91×10⁻⁶. Deltas: [9, 11, 38, 20, 19, 24, 30, 22, 22, 9, 3, 3, 15, 5, 14, 8, 20, 20, 4, 8].

**Other differences between the same pairs at 4×6:**

- total births: +17.2 (20/0);
- pre-shock births: +2.0 (11/5/4, p = 0.21), so most of the effect is post-shock;
- final population: +3.45 (13/7, p = 0.26);
- late harvest: −37.4 (1/19, p = 4.0×10⁻⁵).

**At 2×3:**

- late harvest: −65.6 (1/19);
- final population: −2.1 (4/13/3, p = 0.049, uncorrected).

**What can and cannot be said:**

- This compares "pause rule on (readout from personal experience only)" with "no pause". Thanks to the no-pause diagnostic, it does isolate *the pause rule as implemented*. It does not isolate whether the readout's *content* matters, because no rate-matched random-pause control was run.
- It is post hoc. The pre-specified secondary was OWN against other arms. OWN − NATIVE is +3.74 at 4×6 (18/2, p = 4.0×10⁻⁴).
- It comes with lower harvest. I have not established the mechanism. One hypothesis, not shown: slower descendant movement lowers grazing, which keeps stock above the birth threshold more often.

**Recommended follow-up protocol.** This is written for Rusty and the Designer to approve. I have not run it.

1. Freeze the protocol and publish its hash externally before any run. Use only seeds never used before, chosen by a pre-stated rule (for example 1000–1039). Keep the v2 traces read-only under their current hashes.
2. Use the v2 world, both founder sizes and the 0.7 shock at tick 300. Arms:
   - NATIVE;
   - EMPTY-pause, as in v2;
   - **RANDOM-pause**: same eligibility and alternate-tick rule, with pause probability fixed in advance at the v2 EMPTY rate for each size. Draw it from a *separate* RNG stream so `arng` consumption is unchanged.
   - **ALWAYS-pause**: every eligible move paused, subject to the t−1 rule.
   - OWN, as the inheritance check.
3. Pre-specify primary and harm guard:
   - primary: EMPTY − RANDOM post-shock births per lineage at 4×6, which tests whether the readout's content matters;
   - co-primary: EMPTY − NATIVE at 4×6, to replicate on new seeds;
   - harm guard: late harvest and final population for the same pairs.
   - Success threshold: ≥ 1 birth per lineage, exact two-sided sign test p ≤ 0.05, and no harvest harm beyond a stated margin.
4. Run sensitivity analyses as separate, pre-labelled secondaries, without tuning thresholds:
   - shock multipliers 1.0 (none) and 0.5;
   - positional kernel with torus-correct quadrant distances instead of ordinal IDs.
5. Log the per-tick resource stock and the outcome of the birth-gate test, so the mechanism can be examined rather than guessed.

## 9. Additional scrutiny

- **Tautology check.** `verify_live.py` compares receipts against `runs.json` written by the same code, which is consistency, not correctness. Its census and native-reference checks are genuine. The "byte-for-byte replay" shows determinism, not that the science is correct. My independent audit, the instrumented donor and pause checks, the no-pause equivalence and the 4×6 archived-outcome match add the correctness evidence. (OBS)
- **Positional kernel (DOC/OBS).** Position = `2·(x≥16) + (y≥16)`. Both the `Field` weight (axes 2 and 3 weighted 3) and `Ground.read` use squared ordinal distance. On the 32×32 torus:
  - quadrants 1 and 2 are diagonal but at distance 1;
  - 0 and 3 are also diagonal but at distance 3;
  - 0–2 and 1–3 share an edge but sit at distance 2.
  The kernel mis-states geometry. Same-quadrant matching removes birth-location confounding from the primary contrast, but the readout is still distorted. The "kinetics" axis here is the prediction-error bin (DOC "as v1").
- **Pressure rule.** Pressure is true on about 69–71% of eligible observations. This, not the ground, mainly drives check above 0.5. Pausing makes the agent re-observe the same cell, where its own earlier observation may still be pending. That can feed pressure back into later checks. The alternate-tick rule caps the effect.
- **Field-write fairness.** All live arms write founders and descendants the same way; LEGACY adds a parent-only field. Note that `read_for_direction` also writes a "reading" event (pressure False) every observation. So each observation writes twice, which inflates the encounter channel. This follows the original RT equations. (OBS)

## 10. Output files

All under `/workspace/dc-builder-v2-2026-11-12/`:

- `work/` is the clean extracted pack. It is unmodified: 284 files, SHA256SUMS passes. Two stray `__pycache__` directories created by my reference rebuild were removed.
- `run/` is my working copy:
  - `new_live/` (4 workers) and `new_live_w1/` (1 worker): replay outputs;
  - `instr_live.py` and `instr_out/`: passive instrumentation;
  - `diag_nopause_live.py` and `diag_nopause/`: diagnostic, not scored;
  - `new_receiver/`: demo rerun.
- `live_replay.log`, `live_replay_w1.log`, `verify_packaged.txt`, `verify_repeat.txt`, `receiver_demo_run.txt`.
- `scan/`: `scan.py`, `scan_out.txt`, `hits.json`. The hits file contains hashes and contexts of public material only.
- `audit/`:
  - `audit_traces.py`, `trace_audit.txt`, `trace_audit.json`;
  - `make_instr.py`, `analyze_instr.py`, `instr_analysis.txt`;
  - `donor_and_divergence.py`, `donor_divergence.txt`;
  - `diag_nopause.py`, `diag_nopause.txt`;
  - `native_refs.py`, `native_refs.txt`;
  - `native_4x6_archive.py`, `native_4x6_archive.txt`;
  - `empty_native_extra.txt`;
  - `receiver_attacks.py`.
- `receiver_audit/`: `receiver_audit.txt`, `receiver_audit_log.json`, the test registries and the attack packets. These hold public keys only; no private keys are on disk.

Nothing was published, sent or pushed. The incoming zip still hashes to `7ae94f6d…53d7`.
