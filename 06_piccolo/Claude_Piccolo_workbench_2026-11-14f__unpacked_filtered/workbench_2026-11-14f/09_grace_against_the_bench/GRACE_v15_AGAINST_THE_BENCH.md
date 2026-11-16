# Grace definition v15 laid against what is built

Conductor, 14 Nov 2026, after the keel's three files of 11:27. Readings are marked as readings.

## Why this exists
The conductor asked the keel "which grace goes into the next build: the October grant, the
commons release, or the open hand". The current definition (v15, 13 Nov) was in the conductor's
workspace and had not been opened. Opened, it shows the three are not rivals.

## Four built pieces

| Built piece | Where | What it has (v15 item) | What sits against v15 |
|---|---|---|---|
| Open hand | Nov builds | Reaches all like rain; the brim runs over; passes on through receivers (2, 11, 12, 17) | Inert in ChatGPT v2: no-provision arm gives the same totals |
| Swarm release | commons_v2/sim_v2.py lines 145-153 | Seeks the one stuck longest and sends it toward kin's latest witnessed find (12, K-A). Selection never looks at destination (R5, by construction) | Sets a.d = 0.3 (writes the member's dwelling). Sets a.target (items 2, 9) |
| Signed grant | grace.py, connection.py (24 Oct) | From outside, signed, scoped, bounded in time (1, 13). Fields match the v15 note on what bounds relayed grace | A gate: "missing_grace" refuses the crossing; a second signature by the same owner key. Against R7, "one approval" (Sep), "gate is for authority only" (10 Oct) |
| Grace toy v1 | grace_toy.py (9 Nov) | Fill; landscape unchanged with a probe that can tell; crossing at any barrier weight when ready (2, 3, 4, R2, R3, R7) | One organism. Reading A marked FAIL on R4, which the keel overrode on 13 Nov (K-A) |

Reading: parts of one grace. Item 12 already holds "reaches all" and "seeks the one" together.

## The swarm grace, as written (13 Oct)

    if t % GRACE_EVERY == 0:                       # every 10 ticks
        cand = [a for a in live if a.run >= GRACE_MIN]   # stayed put 15+ ticks
        if cand:
            a = max(cand, key=lambda z: (z.run, -z.id)); fam = fams[a.fam]
            a.d, a.run = 0.3, 0
            fresh = np.where(fam.M > CALL_VALUE, fam.T, -1)
            if fresh.max() >= 0:
                a.target = ... argmax(fresh)       # kin's most recent confirmed find

## Blue sky (not a ruling)
Toy reading A (the unready cross once lifted) and reading B (two keys always) may both hold
once there is more than one organism. Mark 2:3-5, checked in the text 14 Nov: "borne of four";
"When Jesus saw their faith". If those who carry can hold the second key, the unready one
crosses and two keys still turn. Luke 15:5, checked 14 Nov: the shepherd carries the one
himself. The text has both. A one-organism toy can test neither against the other.

## What counts as an encounter (already built, twice)
- Swarm: each tick, (place, value seen, who, when). Shared ground only on a second member's
  confirmation.
- October: Encounter(day, index, place, truncated). "Encounter terrain only. It neither
  interprets nor authorizes."
The yes-or-no fact differs: October's is the owner's reaction. The swarm offers the world's
answer (what I saw differed from what I believed; this already drives dwelling) and another
member's answer (my find was confirmed or not). Neither reaches character today.

## Two toy tests no community build has used
- Outcome times cannot tell filling from a lowered barrier (41 vs 42 at h=1; 229 vs 223 at h=4).
  A probe declared in advance can (-1.29 against -1.27 unchanged; lowered barrier reads -0.67).
- A grantor who picks by destination is caught by a population audit (z 13.4 against 1.8).

## Not built anywhere
- The four pieces in one community.
- A second key held by others.
- "Whole now and not later" (v15 K-D). Nearest: the swarm's moving food and fading family map.

## Open for the keel
- May grace write a member's dwelling?
- Is "toward what kin confirmed" direction from grace, or from family?
- Which yes-or-no fact lays down character in a commons?
- Does the October grant stay a gate, or become the record that grace came from outside?
- Toy questions 2 and 3: does fill carry into the new basin; what counts as "worse".

Toy rerun 14 Nov: results.json 49e579d9a2c636ea26ea79d68b7ecefd3f86d00a4a707a898299a31a0bd7bc1f, byte-identical.
