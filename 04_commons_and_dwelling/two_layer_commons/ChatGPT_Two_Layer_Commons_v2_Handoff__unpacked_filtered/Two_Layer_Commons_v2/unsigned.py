"""Regenerate the inventory of unsigned inside-function writes."""

import argparse
from collections import Counter
import json
from pathlib import Path

from trace import canonical, matching_manifest


def changes(folder):
    for path in sorted(folder.glob("seed_*.json")):
        package = json.loads(path.read_bytes())
        seed = package["seed"]
        yield seed, "FOUNDER", package["alpha"]
        for trial in package["trials"]:
            yield seed, trial["arm"]["name"], trial["beta"]

    for path in sorted(folder.glob("probe_*.json")):
        package = json.loads(path.read_bytes())
        for trial in package["trials"]:
            yield package["seed"], trial["arm"], trial["beta"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, default=Path("UNSIGNED.md"))
    args = parser.parse_args()
    tallies = Counter()
    with args.out.open("x", encoding="utf-8") as handle:
        handle.write("# Every unsigned inside-function write\n\n")
        handle.write("This table gives every committed inside-function field change made without "
                     "a signature. Signed burden releases appear in the raw traces. Choice and "
                     "character writes have their own trace tags. Initialization is the documented "
                     "seed and body defaults. One row represents a committed tick-level state write.\n\n")
        handle.write("| Seed | Arm | Member | Tick | Process | Before | After |\n"
                     "|---:|---|---|---:|---|---|---|\n")
        for folder in args.evidence:
            matching_manifest(folder)
            for seed, arm, member in changes(folder):
                for row in member["ticks"]:
                    for event in row["events"]:
                        if event["layer"] == "function" and event["place"] == "inside" and event.get("signed") is False:
                            tallies[event["process"]] += 1
                            handle.write(f"| {seed} | {arm} | {member['actor']} | {row['tick']} | "
                                         f"{event['process']} | {canonical(event['before'])} | {canonical(event['after'])} |\n")
        handle.write("\n## Counts\n\n")
        for process, count in sorted(tallies.items()):
            handle.write(f"- {process} {count:,}\n")
        handle.write(f"\nTotal {sum(tallies.values()):,}.\n")
    print(f"{sum(tallies.values())} unsigned internal writes")


if __name__ == "__main__":
    main()
