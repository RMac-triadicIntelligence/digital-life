"""Check digests and layer boundaries directly against the raw results."""
import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

from body import Body, PhysicalInputs
from commons import CONDITIONS
from run import GOVERNANCE, HANDS, HARVESTS, MODES, RELEASES, ROOT, TICKS


def checked_files(path):
    manifest = {}
    for line in (path / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        assert name not in manifest and Path(name).name == name
        assert hashlib.sha256((path / name).read_bytes()).hexdigest() == digest, name
        manifest[name] = digest
    assert manifest.keys() == {file.name for file in path.glob("*.json")}
    return manifest


def verify_member(member, config):
    assert len(member["ticks"]) == TICKS
    mode = config["mode"]
    for name, peak in member["peak_occupancy"].items():
        capacity = {"adaptation": 6, "burden": 6, "channel": 8, "choice_history": 72,
                    "deposit": 3, "evidence": 8, "grace_reserve": 6, "hand": 2,
                    "incident_slots": 1, "kernel_basin": 1, "kernel_consumed": 1,
                    "kernel_pending": 1, "kernel_trace": 4, "reserve": 8, "story_slots": 1}
        assert 0 <= peak <= capacity[name], (name, peak)
    for row in member["ticks"]:
        assert row["location"] == [0, 0]
        events = row["events"]
        assert events and all(event["layer"] in ("body", "choice") for event in events)
        assert sum(event["process"] == "grace_channel" for event in events) == 1
        decisions = [event for event in events if event["process"] == "decision"]
        assert all(event["after"]["selected"] in event["after"]["options"] for event in decisions)
        retrieves = [event for event in events if event["process"] == "retrieve_story"]
        if retrieves:
            assert any(event["after"]["topic"] == "history" and event["after"]["selected"] == "ask"
                       for event in decisions)
        if mode == "BODY_ONLY":
            assert not decisions
        if mode == "FROZEN":
            assert all(event["decision_origin"] == "frozen_default" for event in decisions)
            assert not retrieves
        committed = [event for event in events if event["process"] == "protected_commit"]
        for event in committed:
            assert bool(event["signature"]) == event["authorized"] == (event["before"] != event["after"])
            if event["authorized"]:
                assert config["governance"] == "STEWARD_ARM"
                assert event["proposal"]["organism_id"] == member["organism_id"]
        if row["crossing"]:
            assert set(row["crossing"]) >= {"landscape_moved", "noise_present",
                                            "grace_received", "protected_change_authorized"}
        for event in events:
            if event["layer"] == "body" and event["location"] == "inside" and event["before"] != event["after"]:
                assert type(event["signed"]) is bool
                if event["signed"]:
                    payload = event["receipt"]["payload"]
                    assert payload["subject"] == member["organism_id"]
                    assert payload["next_tick"] == row["tick"]
                    assert payload["terrain_write"] == {"burden": event["after"]}


def verify_fixture_key():
    from fixture_ed25519 import PrivateKey, InvalidSignature

    key = PrivateKey(bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"))
    expected = bytes.fromhex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
                             "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")
    assert key.public.raw.hex() == "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    assert key.sign(b"") == expected
    key.public.verify(expected, b"")
    try:
        key.public.verify(expected, b"mutated")
    except InvalidSignature:
        return
    raise AssertionError("altered message accepted")


def verify_grace_never_rewrites_terrain():
    a, b = Body(), Body()
    inputs = (True, 1, 1)
    outcomes = (1, False, False, False, False, False)
    for _ in range(TICKS):
        dry = a.step(PhysicalInputs(*inputs, 0, *outcomes))
        wet = b.step(PhysicalInputs(*inputs, 3, *outcomes))
        for field in ("terrain", "evidence", "settled"):
            assert dry["after"][field] == wet["after"][field]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("--against", type=Path)
    parser.add_argument("--diagnostic", action="store_true")
    args = parser.parse_args()
    path = args.results
    manifest = checked_files(path)
    if args.against:
        assert manifest == checked_files(args.against)
    if args.diagnostic:
        data = json.loads((path / "zero_pulse.json").read_bytes())
        assert hashlib.sha256((ROOT / "DIAGNOSTIC_PREDICTION.md").read_bytes()).hexdigest() == data["prediction_sha256"]
        tally = Counter()
        for trial in data["runs"]:
            beta = trial["beta"]
            verify_member(beta, {"mode": "BODY_ONLY", "governance": "SILENCE"})
            assert beta["metrics"]["grace_received"] == 0
            assert not beta["metrics"].get("release_applied")
            assert beta["metrics"].get("crossings") == beta["metrics"].get("crossings_before_any_grace")
            tally[trial["condition"]] += beta["metrics"].get("crossings", 0)
        assert sum(tally.values()) > 0
        print("PASS", dict(tally))
        return
    verify_fixture_key()
    verify_grace_never_rewrites_terrain()
    protocol = json.loads((path / "protocol.json").read_bytes())
    assert hashlib.sha256((ROOT / "PREDICTIONS.md").read_bytes()).hexdigest() == protocol["predictions_sha256"]
    expected = list(itertools.product(CONDITIONS, MODES, RELEASES, HARVESTS, GOVERNANCE, HANDS))
    count = 0
    for seed in protocol["seeds"]:
        data = json.loads((path / f"seed_{seed}.json").read_bytes())
        verify_member(data["alpha"], {"mode": "ACTIVE", "governance": "SILENCE"})
        assert len(data["trials"]) == len(expected)
        same_tape, same_beta = None, None
        for trial, setting in zip(data["trials"], expected, strict=True):
            config = trial["config"]
            assert tuple(config[name] for name in ("condition", "mode", "release", "harvest", "governance", "hand")) == setting
            reader = trial["beta"]
            verify_member(reader, config)
            observed = [row["opportunity"] for row in reader["ticks"]]
            if same_tape is None:
                same_tape, same_beta = observed, reader["organism_id"]
            assert observed == same_tape and reader["organism_id"] == same_beta
            assert reader["organism_id"] != data["alpha"]["organism_id"]
            count += 1
    assert len(json.loads((path / "summary.json").read_bytes())) == count
    print(f"PASS: {len(manifest)} result digests and {count} matched reader trajectories")


if __name__ == "__main__":
    main()
