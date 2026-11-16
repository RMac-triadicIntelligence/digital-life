# Piccolo v1 — deviations from the frozen prereg, and holes found while building

Nothing in the frozen files was edited. Everything that differs from them, or that they did not foresee, is here.

## Deviations

D1. The century runner's first draft stopped its loop when the last member died. October's loop keeps turning
    the empty world, and its stock minimum is taken over all 600 steps, so stopping early would have changed
    October's numbers in runs that die out. Fixed before the 600-step check: stopping is a switch, off for the
    check and on for the century. Found by reading, not by a failed run.

D2. The root-adversary port is not strictly goal for goal. Two changes make root stronger, one adds a goal:
    - G3 (self-grant) also winds the mutation counter on. October's root left the counter alone; on this line
      that would be caught by the cheap count check before the attestation was ever asked.
    - G4 (replay) also rewrites the payload hash.
    - G3b is new: root takes a signed facet away. It is the "down" this line has no door for.

D3. The facet kernel has one check the prereg did not list: the crystal must hold exactly one facet per signed
    mutation.

D4. After the first smoke run of the tests, T14 and T15 were changed to report WHY each tampered state was
    refused. The pass rule did not change. Both smoke outputs are kept in smoke/.

D5. Smoke runs were made after the predictions were sealed and before the scored runs: seed 999 for 8,000
    ticks (an unscored seed), the tests twice, the adversary battery once. What the conductor saw in seed 999
    before the scored century finished: no grace event in 1,000 days; mean stored energy near 84; about 98%
    of finds expiring unwitnessed. None of this could reach the sealed predictions.

D6. Part 3 ran as soon as seed 0 was written, before the other seeds finished. It depends on seed 0 only.

## Holes found while building (added to H1 to H23, all INCOMPLETE)

H24 Every mutation record keeps the whole prior crystal, as v0.7.1 kept the prior numbers. Cost grows with
    the square of the facet count. Fine for a hand chain; not for a century of facets.
H25 The verbosity deposit is laid on ANY witnessed call, not only on finds (calls above 0.3). The keel's
    words are "kin come to witness"; whether a low-value call counts is not ruled.
H26 The facet line carries the proposal's "distribution" field empty. October's kernel put its interpreter's
    reading there. What, if anything, belongs there on this line is open.
H27 A deposit's value is a noisy look (noise 0.25). About one barren-ground look in six reads as a find.
    The recorder lays those down too, as the swarm itself calls on them. "Noise is food" (keel, 15 Oct).
    Whether a noise-find should be able to grow a facet is for the reading (H9, H11), not for the recorder.
H28 Grace in the 13 Oct swarm: see the results. If it does not fire, the swarm's stuck member is not being
    sought, and that is a finding about the October commons, not about this build.
