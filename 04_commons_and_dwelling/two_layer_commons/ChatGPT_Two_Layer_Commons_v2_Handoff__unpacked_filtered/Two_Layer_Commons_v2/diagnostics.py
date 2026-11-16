"""Predeclared component probes after the unchanged main scoring run."""

import argparse
import json
from pathlib import Path
import tempfile

from character import Shape
from choice import Choice
from dwelling import FacetDwelling, WorldDwelling, dwelling_permissions
from life import simulate
from protocol import ALT_PROFILE, Arm
from run import ROOT
from trace import canonical, digest, dump, matching_manifest
from world import Commons, Legacy, Observation


def isolated_world():
    inside = (0.6, 0.8, 0.0)
    orthogonal = (-0.8, 0.6, 0.0)
    facet = FacetDwelling()
    evolved = WorldDwelling()
    shape = Shape(.6, .5, .5)
    trials = []
    for tick in range(8):
        evolved.step(inside, orthogonal, failed=False)
        active = dwelling_permissions(tick, facet, evolved, None)
        timer = dwelling_permissions(0, None, None, [{"facet": False, "world": active.world_hold}])
        a, b = Choice("ACTIVE"), Choice("ACTIVE")
        sample = Observation(tick, "gate_watch", 1)
        a.observe(sample)
        b.observe(sample)
        trials.append({"tick": tick, "world": evolved.snapshot(), "world_active": active.world_hold,
                       "latency_active": timer.world_hold,
                       "world_decision": a.assess(shape, active),
                       "latency_decision": b.assess(shape, timer)})
    aligned, opposite = WorldDwelling(), WorldDwelling()
    aligned.field = opposite.field = evolved.field
    for tick in range(8, 16):
        aligned.step(inside, inside, failed=False)
        opposite.step(inside, tuple(-value for value in inside), failed=False)
        trials.append({"tick": tick, "aligned": aligned.snapshot(), "antiparallel": opposite.snapshot()})
    return trials


def run(main, output):
    matching_manifest(main)
    expected = (ROOT / "DIAGNOSTIC_PREDICTIONS.sha256").read_text().split()[0]
    assert digest((ROOT / "DIAGNOSTIC_PREDICTIONS.md").read_bytes()) == expected
    protocol = json.loads((main / "protocol.json").read_bytes())
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    files["world_probe.json"] = dump(output / "world_probe.json", isolated_world())
    for seed in protocol["seeds"]:
        evidence = json.loads((main / f"seed_{seed}.json").read_bytes())
        legacy = Legacy.from_wire(evidence["handoff"]["legacy"])
        configurations = (
            Arm("MARGINAL_FULL", history="LISTEN", profile=ALT_PROFILE),
            Arm("MARGINAL_REDACTED", history="LISTEN", profile=ALT_PROFILE, story_variant="REDACTED"),
            Arm("MARGINAL_NO_STORY", condition="GROUND", history="LISTEN", profile=ALT_PROFILE),
            Arm("NO_PROVISION_BODY", choice="BODY_ONLY", grace="NONE"),
        )
        trials = []
        for arm in configurations:
            world = Commons(legacy, arm.condition, arm.story_variant)
            with tempfile.TemporaryDirectory(prefix="commons-v2-probe-") as directory:
                beta = simulate(seed, arm, world, directory)
            trials.append({"arm": arm.name, "beta": beta})
        donor = next(trial["beta"] for trial in evidence["trials"] if trial["arm"]["name"] == "ALT_SEED_LISTEN")
        assert canonical(trials[0]["beta"]) == canonical(donor)
        name = f"probe_{seed}.json"
        files[name] = dump(output / name, {"seed": seed, "trials": trials})
    files["protocol.json"] = dump(output / "protocol.json", {
        "seeds": protocol["seeds"], "python": protocol["python"], "numpy": protocol["numpy"],
        "predictions_sha256": expected,
        "predictions_frozen_utc": (ROOT / "DIAGNOSTIC_PREDICTIONS.frozen_utc").read_text().strip(),
        "primary_summary_sha256": digest((main / "summary.json").read_bytes()),
    })
    (output / "SHA256SUMS").write_text("".join(f"{checksum}  {name}\n" for name, checksum in sorted(files.items())))
    print(f"{len(files)} diagnostic JSON files")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, default=Path("evidence"))
    parser.add_argument("--out", type=Path, default=Path("diagnostic_replay"))
    options = parser.parse_args()
    run(options.main, options.out)


if __name__ == "__main__":
    main()
