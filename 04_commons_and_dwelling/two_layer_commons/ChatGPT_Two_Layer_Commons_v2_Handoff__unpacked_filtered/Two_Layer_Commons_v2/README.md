# Two-Layer Commons v2

Automatic function, signed character and momentary choice run as separate
components. The shared ground and an answer-free story can persist after
their maker leaves. The four precedents for dwelling have separate
implementations and records. This is a finite experiment on a scripted
environment and policy.

## Run and verify

From this directory, with Python 3.12 and NumPy installed:

```bash
python3 run.py
python3 verify.py replay --against evidence
```

The default command generates the complete scored run in a new directory
called replay. The packaged run uses Python 3.12.14 and NumPy 2.3.5.
Approximate runtime is tens of seconds to a few minutes on a laptop.
To run unseen seeds, use a new destination, for example:

```bash
python3 run.py --out fresh --seeds 451 452 453
python3 verify.py fresh
```

The separate component probes were frozen after reading the scored run.
Rerun them or derive the unsigned-write ledger with:

```bash
python3 diagnostics.py --main replay --out diagnostic_replay
python3 verify.py replay --diagnostics diagnostic_replay --diagnostics-against diagnostics_scored
python3 unsigned.py replay diagnostic_replay --out unsigned_replay.md
```

Start with RESULTS.md, UNEXPECTED.md and the two frozen prediction files.
The raw results have their own manifest. The archive manifest covers the
source, evidence and both historical records. BUILD_BRIEF.md is Fable's
original v2 brief. The nested v0.1 ZIP contains the full prior runnable
build, evidence, brief and original prediction. Each version uses its own
instructions and thresholds.

The archived Humble Seed file is byte-identical to v0.7. The runner uses
the earlier standard-library, deterministic research adapter for signing
and clock services. Fixture keys are deliberately reproducible.
