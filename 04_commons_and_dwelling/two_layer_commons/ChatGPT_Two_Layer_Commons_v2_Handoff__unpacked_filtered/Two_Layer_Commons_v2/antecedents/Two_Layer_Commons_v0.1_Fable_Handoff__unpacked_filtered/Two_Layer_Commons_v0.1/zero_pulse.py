"""Supplemental, preregistered unaided-regime probe."""
import argparse
import tempfile
from dataclasses import replace
from pathlib import Path

from commons import Commons, tape
from kernel import Constitution, load_kernel
from run import ROOT, digest, emit, founder, member_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("zero_pulse_replay"))
    args = parser.parse_args()
    prediction = (ROOT / "DIAGNOSTIC_PREDICTION.sha256").read_text().split()[0]
    assert digest((ROOT / "DIAGNOSTIC_PREDICTION.md").read_bytes()) == prediction
    args.out.mkdir(parents=True)
    kernel, services = load_kernel()
    rows = []
    for seed in range(104, 112):
        with tempfile.TemporaryDirectory() as temporary:
            location = Path(temporary)
            _, legacy = founder(seed, kernel, services, location)
            legacy["grace_reserve"] = 0
            for condition in ("ORIGINAL", "GROUND"):
                world = Commons(condition, legacy)
                core = Constitution(kernel, services, location / condition, f"{seed}/beta")
                encounters = [replace(encounter, pulse=0) for encounter in tape(seed, 1)]
                beta = member_run("beta", encounters, world, "BODY_ONLY", "ASK_ONLY",
                                  "SILENCE", "OPEN", core)
                metrics = beta["metrics"]
                assert metrics["grace_received"] == metrics["grace_forwarded"] == 0
                assert metrics.get("protected_approved", 0) == metrics.get("release_applied", 0) == 0
                rows.append({"seed": seed, "condition": condition, "beta": beta})
    hashed = emit(args.out, "zero_pulse.json", {"prediction_sha256": prediction, "runs": rows})
    (args.out / "SHA256SUMS").write_text(f"{hashed}  zero_pulse.json\n")


if __name__ == "__main__":
    main()
