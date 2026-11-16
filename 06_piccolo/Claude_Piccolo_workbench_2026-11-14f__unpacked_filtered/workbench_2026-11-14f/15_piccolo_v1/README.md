# Piccolo v1 — what was built, what it showed, what is still open

14 Nov 2026. Conductor seat (Claude). Keel only until the keel releases it.
The keel's go: "Build with what you have now. The holes leave marked incomplete."

Frozen before any code or run (03:49 UTC):
- PREREG.md 9956871184a4b30e738260c4a7dc2742f0a5f45c22970c16b93784f5d42a71be
- PREDICTIONS_sealed.md 3309d5e71b5227cfdbab14a34452b5a7d0d401c843f03c4ab2d4ebd89ea4d071
- TESTS_facet_line.md 78d7b2a2ce5b7a4b4ed7a667cf9db353f0e76cfe0913acd9d72b68ac729e2379

Marks: RUN (a result of a run here), READ (in a file), KEEL, CONDUCTOR (candidate, not ruled), READING (mine),
INCOMPLETE (a hole).

## What v1 is

1. **The outside.** The 13 Oct commons (V2_FULL), rules unchanged, run for 36,500 days, with read-only deposits.
2. **The seam.** A facet line beside v0.7.1. The owner signs one facet, never a number. v0.7.1 is not edited.
3. **One chain by hand.** A real deposit from the century becomes a signed facet on a real member's crystal.

## What v1 is not

It raises no proposal by itself (H9). A facet changes nothing a member does (H11). No grant, no basin, no
reader is joined. The bench key that signed in Part 3 is not the keel's. 28 holes are listed and left open.

## Part 1 — the commons for a hundred years (RUN)

Check first: the new runner equals October's stored results at 600 steps in 58 of 58 checks (all 20 seeds of
V2_FULL, the other seven variants on seeds 0 to 4, and with the recorder off). It also equals October's own
unedited function at 20,000 ticks on seeds 0 and 1. Seed 0's century, run twice, is byte-identical
(420bc938b6fbfaec3bb5a66ff84e1c13136d6e90b8b8f6dd1c122dce7acd6a3a).

Seeds 0 to 10 finished inside the window (eleven seeds, none dropped). results_century.json receipt
dee6f09cea875e667255a4b80e7dab43bb1294f4ffba1c666b8a5a856ff5086f.

| Measure | Across the 11 seeds |
|---|---|
| Alive on day 36,500 | 11 of 11 |
| Members at the end / peak | 37 to 49 / 42 to 62; safety cap never hit |
| Founding lineages alive | 4 of 4 in every seed |
| Oldest living member born | day 0 in every seed |
| Founders alive at the end | 8 (7 in one seed), every one of them a scout |
| Members ever born in the century | 118 to 179 |
| Median life of those who died | 6 to 10 days |
| **Keepers alive at the end** | **0 in every seed** |
| Keepers ever born / dead | 78 to 119 / all of them |
| Scouts ever born / dead | 40 to 60 / 3 to 12 |
| Stored energy at the end (median) | 1,681 to 4,229 (a member starts with 1) |
| Food stock, lowest point | 14% to 16% of the starting stock |
| Finds laid out | 1.73 to 2.09 million per seed |
| Finds that expired unwitnessed | 97.5% to 98.7% |
| Distance to nearest kin when laid: witnessed / expired | 2.6 to 2.8 / 5.2 to 6.6 cells |
| Ranging on unknown ground that found food | 16% to 18% |
| **Grace events** | **0 in every seed** |
| Scouts' / keepers' mean curiosity share of deposits | 0.57 to 0.74 / 0.16 to 0.34 |
| Colour distance between living members of one household | 0.012 to 0.028 |
| Same-colour pairs that lie in different places | 0% in every seed (mean place overlap 0.90) |
| Households whose pooled spectrum is fuller than their most even member's | 0 of 76 |

### Four things nobody predicted (RUN)

1. **Only scouts live.** On day 36,500 every living member is a scout, in 11 of 11 seeds. Every keeper ever
   born has died. This is already most of the way there at October's own horizon: at 600 steps the 20 October
   runs have 0 to 9 keepers left among 20 to 35 scouts, and by one year there is no keeper in any of 10 seeds
   checked. The October result (the commons holds with roles) was read off a population that was already
   almost all scouts.
2. **The membership freezes.** After the first year births and deaths are rare: 21 to 48 births and 15 to
   40 deaths per seed in the remaining 99 years. About forty scouts, eight of them founders, live the whole
   century. They do not age, and their stored energy climbs every decade. The only energy that ever passes
   from one member to another is the half unit a parent gives a newborn.
3. **Grace never happens.** The swarm's grace step needs a member to have stayed 15 ticks. In a century, on
   11 seeds, it fired 0 times. In October's own 20 runs at 600 steps it also fired 0 times; the longest stay
   in any of them was 9 ticks. The 13 Oct commons has always run without its grace.
4. **A century makes the living alike.** In raw lifetime deposits the living members end nearly one colour
   and nearly one map of places. Totals wash out. What still tells two members apart is not how much, it is
   which deposit, where, on what day — which is what a facet records and a total does not.

### READING, untested

- Why keepers die is not established. One candidate from the code: copying from the family map fades with
  experience (weaning), so an older keeper steers by its own stale, noisy belief while the food moves every
  150 ticks; a scout never uses belief to steer, it reads the family's confidence map. The October bench
  already has a NO_WEANING variant; a century of it would test this. Not run.
- For Piccolo: as the outside stands, a keeper's character could never grow. It dies in days. Any joining of
  character to the commons would be joining it to scouts only. This is the keel's to weigh before H9.

## Part 2 — the facet line (RUN)

- Kernel: piccolo_facet_kernel_v0_1.py 9b4b9a2e8775d4854d66e1b1cd5132ed7e0301aecd325368bcb2b44c05704c04, made
  from v0.7.1 by make_facet_kernel.py; diff in FACET_KERNEL.diff. v0.7.1 unchanged (8b849cd0...d367b).
- Constitution hash on this line: cef31059e361efd46dffc3af60d322886cb791ccf383c6684f7fb8ee40887986
  (v0.7.1: ecb000bdd3c61b3d5f136c6f8b8f55ba4af2dd56b7c056fb4cc02171f5572d14). A new birth line.
- Tests T01 to T23: 23 of 23 PASS, run twice, byte-identical. Receipt
  e0fa82960a8634803264289dba95f9b30c12a3b0f1779094f6c1113a83e74bcf.
  Nothing lands unsigned. A signed facet cannot be dropped, altered, reordered or added to without the state
  refusing to load. Stale, expired, replayed, forged, cross-face and numeric proposals are refused.
- Root-adversary battery, ported: the same pattern as v0.7.1 in October. Held: G1, G1b, G2, G3, G3c, G4, G7,
  G7b, and the new G3b (root takes a facet away). BREACHED: G6 (a forged ordinary event in the tail) always;
  G5 (rollback) when the witness is lost. Those two are open on v0.7 and v0.7.1 as well. Not closed here.
  Receipt aab02bb68ebf969bda773e8f192afd964f7c4dfc1ddabafd882327a1d32a1f0c.

## Part 3 — one member, one chain (RUN)

Seed 0, member 0: a founder and a scout, born day 0, alive on day 36,500, with 36,179 curiosity deposits,
13,619 verbosity, 16,622 formality, 168,374 ranging looks that found nothing, and no grace.
Its first deposit of each kind (all on day 0) became a facet. Each proposal changed nothing until signed.
The crystal holds three facets, loads, attests and audits. Crystal root
fd2df84a7b7be7d5f812ac035df8e0547ca04138dab60bdce898d47f7f39586c. Run twice, byte-identical
(949b018d1ee8a798d67e6d7ec9f8afcf5cedd09582fcfbf3de2d2cf7377184d1).

## The conductor's sealed predictions, scored

See SCORING.md. 17 held, 3 missed. The four results above were not among them.

## Holes — INCOMPLETE

H1 to H23 are in PREREG.md section 3. H24 to H28 were found while building and are in DEVIATIONS.md.
The ones that stop Piccolo from being an organism: H9 (which deposits become a proposal), H11 (what a facet
does), H13 (who the owner is, and when), H4 (how long a proposal lives in commons days), H8 (whether readiness
leaks under "no down"). And now, from the run: what the outside is, if only scouts live in it.

## Run it

    python3 check_600.py                 # must print PASS before anything else is trusted
    python3 run_century.py century       # 36,500 days, October's seeds in order, two at a time
    python3 analyse_century.py century results_century.json
    python3 make_facet_kernel.py && python3 test_facet_line.py && python3 adversary_facet.py
    python3 hand_chain.py century/seed_00.json results_hand_chain.json
    python3 diag/diag_grace_and_long_run.py && python3 diag/diag_roles_at_600.py

Needs Python 3 with numpy and cryptography. Nothing here is evidence of anything quantum, and nothing is a
claim about consciousness.
