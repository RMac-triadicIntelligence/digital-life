# Piccolo v1 — pre-registration

Frozen 14 Nov 2026, before any code for this build was written and before any run.
Conductor seat (Claude). The keel's go: "Build with what you have now. The holes leave marked incomplete." (14 Nov, 21:41)

This file says what is built, on whose word each piece stands, what is measured, and what is NOT built.
Nothing here fills a hole. A hole is named and left open.

Standing marks: KEEL (his ruling or his words), BENCH (already built and run by him or reproduced here),
CONDUCTOR (my candidate, not ruled), INCOMPLETE (a hole, left open).

## 1. What Piccolo v1 is

Three parts and a list of holes.

**Part 1. The outside: the commons for one hundred years.**
The 13 Oct swarm (commons_v2, variant V2_FULL), rules unchanged, run for 36,500 days.
- 36,500 days: KEEL (14 Nov 21:00).
- One day = 8 swarm ticks, so 292,000 ticks: CONDUCTOR (given 21:00, kept by the keel at 21:23).
- Run the unchanged swarm for the century first, predictions sealed: CONDUCTOR, agreed by the keel at 21:23.
- Source files, hashed: sim_v2.py b5cbf3b5b6194a7f2930645e7c02742009abf8f7c1de2926248bd98af5ca2e73;
  sim.py (v1 constants and world) 128682a18b056b1fafeb1628b14b7eb576e37f4e9406974ef616a512e08ea777;
  October prereg d96565a60452c81bd2ee3584419a05c366af289342855d6b6fb55ce6d4a62401. BENCH.
- The October run function is fixed at 600 steps. The century runner is a copy of that function with the
  length made a parameter and read-only recorders added. Two housekeeping changes, both required to make a
  century possible and both claimed to change nothing a living member does: dead members are dropped from the
  working list (order of the living unchanged), and households with no living member are dropped.
  CHECK before any century run: at 600 steps the new runner must return exactly October's stored results
  (results.json, per_seed) for all 20 seeds of V2_FULL, and must equal the original function's output on the
  other seven variants for seeds 0 to 4. If it does not, the century is not run.

**Part 1b. Deposits (read-only).**
"There is no yes-or-no facts. Same as October." KEEL. An encounter is not a verdict; it is laid down where and
when it happened. The recorder lays down, per member, per place, per day:
- every observation (count only);
- three kinds of relevant encounter, from the table the keel kept at 21:09 ("Keep everything the same except
  in all three categories there is no down"):
  - curiosity: "up when ranging finds food";
  - verbosity: "up when kin come to witness";
  - formality: "up when the ground is as the family said".
- nothing is laid down as a failure, and nothing counts against a member. KEEL (no down; no penalty in no success).
The words are the keel's. The operational definitions in swarm terms are CONDUCTOR, built only from thresholds
the October swarm already has:
  - curiosity deposit: the member moved on its last turn (run == 0), the family's confidence in this cell is
    at or below 0.2 (the swarm's own known-ground line), and what it observes is above CALL_VALUE (0.3).
  - verbosity deposit: a call this member laid out is witnessed by kin (the swarm's own witness rule).
    Laid at the place of the call, on the day it is witnessed, to the member who called.
  - formality deposit: the family's confidence in this cell is above 0.2 and what the member observes is
    within WITNESS_TOL (0.3) of what the family map says.
- also counted, as base rates and never as a mark against anyone: ranging on unknown ground that found
  nothing; finds laid out (calls above CALL_VALUE); finds witnessed; finds that expired unwitnessed, with
  the place and the distance to nearest kin when laid; grace received; births; deaths.
The recorder draws no random numbers and writes to nothing the swarm reads.

**Part 2. The seam: a facet line beside v0.7.1.**
- Kernel v0.7.1 with v0.7 as control: KEEL (19:27). v0.7.1 file 8b849cd0710c8c33a0657f09b65da71ff7bf933d9ed3e947ec27f91e297d367b
  is not edited. BENCH.
- "A rule change goes in as a new build beside the old one." KEEL. The facet line is a separate file made
  from the v0.7.1 source by a recorded patch; the diff is kept.
- Not a counter; a crystal prism: KEEL (21:13). No down: KEEL (21:09). Nothing moves unsigned: KEEL-agreed.
- What the owner signs on this line: one facet, not a number. CONDUCTOR (recommended 21:23 reply; not ruled).
  facet = {place: [x, y], day: n, grown_from: sha256 of the deposit it grew from}.
  character = for each of the three faces (verbosity, formality, curiosity; list unchanged), an ordered list
  of signed facets. The only way the list changes is one append through the owner's signature.
  There is no proposal shape that removes or alters. No value range. No cap.
- Kept from v0.7.1 without change: owner key outside the organism; signature bound to the exact change, its
  evidence and the state it was read from; stale, expired, replayed, forged and cross-category proposals
  refused; first-commit flag; owner attestation of every result; fail-closed load; witness outside; I1 and I2.
- Removed on this line: the keyword interpreter and its one sanctioned move (down by 0.25).
- Constitution wording on this line: CONDUCTOR draft. Its hash will differ from ecb000bd...2d14. This is a
  new birth line, not a patch.
- Tests T01 to T23 (listed in tests file, written before the kernel is run) and the 16 Oct root-adversary
  battery ported to this line (all ten goals).

**Part 3. One member, one chain, by hand.**
From century seed 0: the lowest-numbered member alive on day 36,500. Its first deposit of each of the three
kinds becomes a facet proposal; a bench owner key signs; the result is attested and audited.
The owner key here is a bench key made by the test. The keel has signed nothing. This shows the path
deposit -> proposal -> signature -> crystal -> audit with real data. It does not show which deposits ought
to become proposals (hole H9).

## 2. What is measured in the century (per seed)

M1 survival to day 36,500. M2 population at the end, peak, safety cap. M3 founding lineages alive (of 4).
M4 birth day of the oldest living member at the end; founders alive.
M5 finds laid, witnessed, expired unwitnessed. M6 mean distance to nearest kin when laid, witnessed against expired.
M7 member colour: for members with at least 30 relevant deposits, the proportions (curiosity, verbosity,
   formality) of their deposits. This is an unsigned reading of raw deposits. It is not character.
   Scouts (id divisible by 3, as October) against keepers.
M8 mean distance between members' colours within a household, living members at the end.
M9 household against member: entropy of the household's pooled proportions against its most even member's.
M10 same colour, different place: among living qualifying members at the end, pairs whose colours differ by
    less than 0.05 (L1): the share whose places overlap by less than 0.5 (histogram intersection of where
    their relevant deposits lie).
M11 base rate: of ranging observations on ground unknown to the family, the share that found food.
M12 grace events and distinct receivers.
M13 identity: the 600-step check above; seed 0 run twice and compared byte for byte.
Yearly snapshots (365 days) of population, households, lineages, stock, births, deaths, finds, grace.

Seeds: the October seeds in order 0, 1, 2, ... Two run at a time. Seeds are started in order until a
35-minute window closes; those in flight finish. Every seed that finishes is reported. None is dropped.

## 3. Holes — INCOMPLETE, not filled

H1  What "good" is read from (grace item 7). Unruled.
H2  Whether "from outside" stays fixed beside it (item 1). Unruled.
H3  "or steer" in item 7. Unruled.
H4  Staleness and liveness. The kernel's proposal life is 3,600 wall-clock seconds, as v0.7.1. How that maps
    onto commons days, and the owner's presence over a hundred years, are unruled. Not built.
H5  The October grant as a gate in the commons. No grants are issued in v1. Not joined.
H6  The five questions left open in the 25 Oct repair pack.
H7  "Not ready + grace -> the basin is filled" (9 Nov) against the 25 Oct build, which empties it. Unbuilt.
H8  Whether readiness leaks under "no down" (the 25 Oct basin drifts down 0.05 a day and is pushed back). Unruled.
H9  The proposer: which deposits become a proposal (basin, fresh look, look-back), per face. NOT JOINED.
    Piccolo v1 raises no proposal by itself.
H10 Which place a facet takes when a look passes.
H11 The reading: facets + where the member stands + the side the light comes from -> colour -> what the
    member does. NOT BUILT. In v1 a facet changes nothing a member does. The commons runs as October.
H12 Which side of the light meets which face (ground, kin, above). Blue sky. Unruled.
H13 The owner: one or many; who owns a newborn; when the owner is present.
H14 Whether a member is born with a first cut or a name. Birth crystal is empty in v1.
H15 The counter control arm (v0.7.1 numbers, up only). NOT RUN: it needs H9. The claim that it ends white
    is arithmetic and is not scored here.
H16 Every member a kernel organism born through the one door. NOT JOINED. One member is shown by hand.
H17 Dwelling-form placements; character as its own layer; the conscious and unconscious layers. Not represented.
H18 The salt (Matthew 5:13). Not squared with "no down".
H19 Unwitnessed finds. Measured only.
H20 The three operational definitions in Part 1b are the conductor's.
H21 The facet line's constitution wording is the conductor's draft.
H22 v0.7 (01db270a) as kernel control for the facet line. The facet line is derived from v0.7.1 only.
H23 No seat has reproduced any of this.

## 4. What would count against this build

- The 600-step check fails: the runner is not October's swarm and Part 1 is void.
- Seed 0 does not reproduce byte for byte.
- Any test in which a facet lands without the owner's signature, or an earlier facet changes or disappears
  and the state still loads and audits.
- The v0.7.1 file hash changes.

No result here is evidence of anything quantum, and none is a claim about consciousness.
