"""One-command deterministic founder/reader experiment and signed evidence handoff."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

import numpy as np

from kernel import SOURCE_HASH
from protocol import Arm, DEFAULT_SEEDS, TICKS, arms, describe
from trace import digest, dump
from world import Commons, Legacy

ROOT = Path(__file__).resolve().parent
MAX_SEEDS = 64
LEGACY_WIRE_BYTES = 2048


def read_legacy(path):
    with Path(path).open("rb") as source:
        data = source.read(LEGACY_WIRE_BYTES + 1)
    if len(data) > LEGACY_WIRE_BYTES:
        raise ValueError("oversized legacy handoff")
    return Legacy.from_wire(json.loads(data))


def founder(seed, output, legacy_output):
    from life import simulate

    empty = Legacy((0, 0, 0), (0, 0, 0), None)
    world = Commons(empty, "ORIGINAL")
    with tempfile.TemporaryDirectory(prefix="commons-founder-state-") as directory:
        alpha = simulate(seed, Arm("FOUNDER", condition="ORIGINAL"), world, directory, founding=True)
        legacy = world.freeze_legacy().wire()
        alpha["legacy_publication"] = {
            "actor": "alpha", "layer": "choice", "place": "outside", "tick": TICKS,
            "process": "keep_answer_free_story", "bells": list(world.repeated_observations),
            "story_sha256": digest(legacy["story_text"].encode()) if legacy["story_text"] else None,
        }
    # Founder kernel and witness files have been removed before transfer.
    dump(output, alpha)
    dump(legacy_output, legacy)


def make_yoke(donor):
    return [
        {"facet": tick["dwelling"]["facets"]["active"],
         "world": tick["dwelling"]["world"]["active"],
         "basin": tick["dwelling"]["uncertainty_basin"]["active"],
         "seam": tick["dwelling"]["commitment_point"]["active"]}
        for tick in donor["ticks"]
    ]


def reader(seed, legacy_path, output):
    from life import simulate

    legacy = read_legacy(legacy_path)
    trials = []
    yokes = {}
    for arm in arms():
        source = "BOTH" if arm.name == "LATENCY" else "RANDOM"
        yoke = yokes[source] if arm.dwelling == "LATENCY" else None
        world = Commons(legacy, arm.condition, arm.story_variant)
        ground_at_entry = world.ground()
        with tempfile.TemporaryDirectory(prefix="commons-reader-state-") as directory:
            beta = simulate(seed, arm, world, directory, yoke=yoke)
        if arm.name in ("BOTH", "RANDOM"):
            yokes[arm.name] = make_yoke(beta)
        trials.append({"arm": asdict(arm), "initial_ground": ground_at_entry, "beta": beta,
                       "latency_donor": source if yoke else None})
    dump(output, trials)


def worker(role, seed, workdir, legacy, result):
    argv = [sys.executable, str(ROOT / "run.py"), "--worker", role, str(seed),
            str(legacy), str(result)]
    subprocess.run(argv, cwd=workdir, check=True)


def protocol_hash():
    expected = (ROOT / "PREDICTIONS.sha256").read_text(encoding="utf-8").split()[0]
    if digest((ROOT / "PREDICTIONS.md").read_bytes()) != expected:
        raise RuntimeError("frozen predictions digest mismatch")
    return expected


def run(output, seeds):
    prediction = protocol_hash()
    output.mkdir(parents=True, exist_ok=False)
    files, summaries = {}, []
    for seed in seeds:
        with tempfile.TemporaryDirectory(prefix="commons-legacy-") as directory:
            scratch = Path(directory)
            founder_trace = scratch / "alpha.json"
            reader_trace = scratch / "beta.json"
            legacy = scratch / "handoff.json"
            # The reader's world starts after the predecessor exits and its
            # private stores vanish. Only the wire artifact crosses that line.
            worker("founder", seed, scratch, legacy, founder_trace)
            with tempfile.TemporaryDirectory(prefix="commons-reader-process-") as reader_directory:
                active = Path(reader_directory)
                reader_legacy = active / "legacy.json"
                reader_output = active / "readers.json"
                reader_legacy.write_bytes(legacy.read_bytes())
                worker("reader", seed, active, reader_legacy, reader_output)
                reader_trace.write_bytes(reader_output.read_bytes())
            trials = json.loads(reader_trace.read_bytes())
            alpha = json.loads(founder_trace.read_bytes())
            bridge = {"founder_removed_before_reader": True, "separate_processes": True,
                      "legacy": read_legacy(legacy).wire(), "wire_sha256": digest(legacy.read_bytes())}
            for trial in trials:
                beta = trial["beta"]
                readings = [{"tick": read["tick"], "sha256": read["sha256"],
                             "interpretation": read["interpretation"], "character": read["character"]}
                            for read in beta["story_readings"]]
                summaries.append({
                    "seed": seed, "arm": trial["arm"]["name"], "initial_ground": trial["initial_ground"],
                    "initial_character": beta["initial_character"], "final_character": beta["final_character"],
                    "story_readings": readings, "peak_occupancy": beta["peak_occupancy"],
                    "phase_end_commitment": beta["phase_end_commitment"], **beta["metrics"],
                })
            name = f"seed_{seed}.json"
            files[name] = dump(output / name, {"seed": seed, "handoff": bridge,
                                              "alpha": alpha, "trials": trials})
    files["summary.json"] = dump(output / "summary.json", summaries)
    files["protocol.json"] = dump(output / "protocol.json", {
        **describe(), "seeds": list(seeds), "python": platform.python_version(),
        "numpy": np.__version__, "kernel_sha256": SOURCE_HASH, "predictions_sha256": prediction,
        "prediction_frozen_utc": (ROOT / "PREDICTIONS.frozen_utc").read_text().strip(),
    })
    (output / "SHA256SUMS").write_text("".join(f"{value}  {key}\n" for key, value in sorted(files.items())))
    print(f"{len(seeds)} founders, {len(summaries)} readers, {len(files)} result files")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        _, _, role, number, legacy, output = sys.argv
        if role == "founder":
            founder(int(number), Path(output), Path(legacy))
        elif role == "reader":
            reader(int(number), Path(legacy), Path(output))
        else:
            raise ValueError("unknown worker")
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("replay"))
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    options = parser.parse_args()
    if (len(set(options.seeds)) != len(options.seeds) or min(options.seeds) < 0
            or len(options.seeds) > MAX_SEEDS):
        parser.error(f"provide 1–{MAX_SEEDS} distinct nonnegative seeds")
    run(options.out.resolve(), options.seeds)


if __name__ == "__main__":
    main()
