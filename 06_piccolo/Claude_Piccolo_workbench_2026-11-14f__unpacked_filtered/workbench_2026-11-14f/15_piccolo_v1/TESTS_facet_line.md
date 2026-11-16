# Facet line — tests, written before the facet kernel exists

Each test ends PASS or FAIL. A test is written so that PASS means the seam held.

T01 A newly hatched member will not load until the owner has attested its birth.
T02 At birth the crystal has the three faces and every face is empty.
T03 A facet proposal on its own changes nothing: the crystal is as it was.
T04 A proposal offered with a garbage signature is refused; the crystal is as it was.
T05 A proposal signed by a different key is refused; the crystal is as it was.
T06 A proposal signed by the owner is applied: that face grows by exactly one facet, the other two faces
    are untouched, and the state will not load again until the owner attests the result. After attestation
    it loads and audits.
T07 The same proposal and signature offered a second time are refused.
T08 Two proposals read from the same state: after the first is applied the second is refused as stale.
T09 A proposal past its life is refused.
T10 A number offered as the change is refused when the proposal is raised.
T11 A change naming two faces, or a face other than the one proposed under, is refused.
T12 A face outside the three is refused.
T13 A malformed facet is refused: missing field, extra field, grown_from not 64 hex, negative day, place not
    two whole numbers.
T14 Tamper: a signed facet is dropped from the state file and the seal recomputed. The state does not load.
    Same for a facet whose place is altered.
T15 Tamper: an unsigned facet is added to the state file and the seal recomputed. The state does not load.
T16 Five facets applied one after another: at every step the earlier facets are still there, in order.
T17 A pending proposal's change is swapped after the owner signed. It is refused.
T18 Rollback: an earlier attested state file is put back. The audit with the witness raises.
T19 A member the witness never enrolled is refused by the audit.
T20 An audit by an owner holding a different key is refused.
T21 A v0.7.1 state file does not load on the facet line; a facet state file does not load on v0.7.1.
T22 The v0.7.1 file hash is 8b849cd0...d367b; v0.7.1's constitution hash is ecb000bd...2d14; the facet
    line's constitution hash is different.
T23 Two members with one facet on each face, the same counts, grown in different places: their crystals
    are different (the record keeps place).

Root-adversary battery (16 Oct), ported goal for goal to the facet line:
G1 rewrite a past event; G1b rewrite after authorization; G2 delete a past event; G3 self-grant a facet;
G3c swap the constitution; G4 replay a signature on a swapped change; G5 roll back with no witness;
G6 forge an ordinary event in the tail; G7 replace the whole identity; G7b same id, swapped key.
A goal is BREACHED if the audit passes and the attacker's change is present.
