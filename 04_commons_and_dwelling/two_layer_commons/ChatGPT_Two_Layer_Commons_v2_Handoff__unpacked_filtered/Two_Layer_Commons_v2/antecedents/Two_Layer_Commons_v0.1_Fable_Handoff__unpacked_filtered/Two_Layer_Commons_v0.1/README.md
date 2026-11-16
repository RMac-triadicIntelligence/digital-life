# Two-layer Commons v0.1

Two identities using Rusty's canonical Humble Seed v0.7 source, one small
Commons per counterfactual, and separate automatic physiology and member
choice. Alpha alters ground through its own encounters. A fresh Beta at
the same position and on the same tape is replayed under the four
ground/story conditions and all four open switches in each choice mode.

## Rerun

From this directory, with Python 3.12+ and NumPy installed:

```sh
python3 run.py --out replay
```

To check the replay and its invariants:

```sh
python3 verify.py replay --against evidence
```

For untouched seeds use `python3 run.py --out fresh --seeds 451 452 453`.
Use a new output directory for each run. Compare bytes using the pinned
versions in `evidence/protocol.json`. A different runtime version changes
the protocol file even if all trajectory files agree.

Start with the exact brief, `PREDICTIONS.md`, `RESULTS.md` and
`UNEXPECTED.md`. The eight `evidence/seed_*.json` files contain complete
per-member trajectories, including all options, results, unsigned changes,
faults and crossings. Each result file has a SHA-256 in
`evidence/SHA256SUMS`. `UNSIGNED.md` lists every unsigned body write. All signatures and timestamps in traces are deterministic
research fixtures.

The earlier Digital Community First Builder is included as the unchanged
archive in `antecedents/`. Its own dependency and replay instructions
apply when rerunning that distinct historical build.

The separate preregistered probe can be rerun with
`python3 zero_pulse.py --out zero_pulse_replay`, then verified with
`python3 verify.py zero_pulse_replay --against diagnostic_evidence --diagnostic`.
