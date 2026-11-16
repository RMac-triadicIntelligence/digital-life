"""Independent evidence checks and protocol falsifiers for the v2 handoff."""

import argparse
import base64
from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile

from body import Body, PhysicalInputs, RESERVE_CAPACITY, ADAPTATION_CAPACITY, BURDEN_CAPACITY, PUMP_CAPACITY
from character import CharacterTerrain, OwnerPort
from choice import DECISION_CAPACITY
from dwelling import BASIN_CAPACITY
from fixture_ed25519 import InvalidSignature, PrivateKey, PublicKey
from kernel import Constitution, SOURCE_HASH, load_kernel
from protocol import ALT_PROFILE, Arm, REARING_TICKS, SILENCE_START, SIGNING_TICKS, TICKS, arms, opportunities
from run import ROOT, make_yoke, protocol_hash, read_legacy
from trace import ROW_CAPACITY, canonical, digest, matching_manifest
from world import HAND_CAPACITY, REDACTED, CHANNEL_CAPACITY, SILT_CAPACITY, POOL_CAPACITY, STORY_BYTES

CAPACITIES = {
    "body.reserve": RESERVE_CAPACITY, "body.adaptation": ADAPTATION_CAPACITY, "body.burden": BURDEN_CAPACITY, "body.hand": HAND_CAPACITY,
    "body.steady": 1, "pump.strokes": PUMP_CAPACITY, "world.channel": CHANNEL_CAPACITY,
    "world.silt": SILT_CAPACITY, "world.provision_pool": POOL_CAPACITY, "world.incident": 1,
    "world.bell_witnesses": 2, "world.story": STORY_BYTES,
    "facet_dwelling.coordinates": 3, "facet_dwelling.field": 1, "world_dwelling.field": 1,
    "basin.category": BASIN_CAPACITY, "choice.decisions": DECISION_CAPACITY, "choice.source_values": 2, "choice.interpretation": 1,
    "choice.current_case": 1, "choice.standing": 1, "commitment_point": 1, "kernel.pending": 1,
    "kernel.basin": 0, "kernel.consumed": 5, "kernel.trace": 12, "kernel.character": 3,
    "kernel.checkpoint": 1, "kernel.witness": 1, "kernel.gates": 3, "kernel.birth": 1,
    "observer.tape": TICKS, "observer.events_per_tick": ROW_CAPACITY,
}
DWELLING = ("facets", "world", "uncertainty_basin", "commitment_point")


def refuse(action, expected):
    try:
        action()
    except expected:
        return
    raise AssertionError("negative control unexpectedly passed")


def verify_fixture():
    private = PrivateKey(bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"))
    signature = bytes.fromhex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
                              "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")
    assert private.public.raw.hex() == "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    assert private.sign(b"") == signature
    private.public.verify(signature, b"")
    refuse(lambda: private.public.verify(signature, b"modified"), InvalidSignature)


def verify_port_isolation():
    dry, wet = Body(), Body()
    base = PhysicalInputs(True, 1, 2, 1, False, False, False, "HEALTHY", (), False, False, False)
    for tick in range(TICKS):
        a = dry.step(base)
        b = wet.step(replace(base, provision=tuple(f"{tick}.{i}" for i in range(3))))
        for field in ("reserve", "adaptation", "burden", "steady"):
            assert a["after"][field] == b["after"][field]
        assert a["boundary"] == b["boundary"]
        assert a["pump"] == b["pump"]


def verify_handoff_schema(wire, directory):
    path = Path(directory) / "invalid.json"
    assert wire == json.loads(canonical(wire))
    for extra in ("founder_character", "interpretation", "owner_permission", "founder_body", "answer"):
        path.write_text(canonical(wire | {extra: [1]}))
        refuse(lambda: read_legacy(path), ValueError)
    for changed in ({"channel": [0, True, 0]}, {"silt": [0, 0]}, {"channel": [7, 0, 0]},
                    {"story_text": {"answer": 1}}, {"story_text": "x" * 241}):
        path.write_text(canonical(wire | changed))
        refuse(lambda: read_legacy(path), ValueError)


def verify_seam_attacks(directory):
    module, services = load_kernel()
    root = Path(directory)
    a = Constitution(module, services, root / "a", "audit-a")
    ta = CharacterTerrain(a)
    b = Constitution(module, services, root / "b", "audit-b")
    tb = CharacterTerrain(b)
    view = {"category": "curiosity", "leader": "favor_first",
            "distribution": {"favor_first": .82, "favor_second": .12, "unmodeled_cause": .06},
            "evidence": [{"context": "a"}, {"context": "b"}]}
    first = ta.propose(view)
    other = tb.propose(view)
    first_signature = a.sign(first.payload_to_sign)
    assert b.seed.authorize_and_apply(other.proposal_id, first_signature) is None
    b.seed.verify()
    assert tb.shape().curiosity == .6

    state = a.seed._state_path().read_bytes()
    first.evidence[0] = "substituted after signature"
    assert a.seed.authorize_and_apply(first.proposal_id, first_signature) is None
    assert ta.shape().curiosity == .6
    a.seed._state_path().write_bytes(state)
    a.seed.load()
    a.witness.check_current(a.seed.checkpoint)

    valid = a.seed.authorize_and_apply(first.proposal_id, first_signature)
    assert valid is not None
    a.attest(valid)
    assert a.seed.authorize_and_apply(first.proposal_id, first_signature) is None
    a.seed.verify()
    assert ta.shape().curiosity == .675
    new_state = a.seed._state_path().read_bytes()
    a.seed._state_path().write_bytes(state)
    a.seed.load()
    refuse(lambda: a.witness.check_current(a.seed.checkpoint), module.RollbackDetected)
    a.seed._state_path().write_bytes(new_state)
    a.seed.load()
    a.witness.check_current(a.seed.checkpoint)

    owner = OwnerPort(a, SIGNING_TICKS, SILENCE_START, False)
    incident = {"issue": "fixture"}
    assert owner.offer_release(6, incident, "turn_and_approach", "ASK_ONLY") is None
    assert owner.offer_release(15, incident, "ask_for_release", "ASK_ONLY") is None
    receipt = owner.offer_release(6, incident, "ask_for_release", "ASK_ONLY")
    assert receipt is not None
    refuse(lambda: owner.check_release(8, incident, receipt), ValueError)
    assert owner.check_release(7, incident, receipt)
    refuse(lambda: owner.check_release(7, incident, receipt), ValueError)


def check_signature(key, payload, signature, kernel=False):
    text = canonical(payload)
    # The canonical v0.7 serializer and this observer agree for these inputs.
    assert not kernel or payload["schema_version"] == "0.7"
    key.verify(base64.urlsafe_b64decode(signature), text.encode())


def check_member(beta, arm, seed, legacy, signature_cache, ordinal):
    assert beta["actor"] == ("alpha" if ordinal == 0 else "beta")
    assert beta["birth_position"] == 0 and beta["kept_after_reload"] is True
    assert len(beta["ticks"]) == TICKS and beta["metrics"]["body_ticks"] == TICKS
    assert beta["peak_occupancy"].keys() == CAPACITIES.keys()
    for store, fullness in beta["peak_occupancy"].items():
        assert 0 <= fullness <= CAPACITIES[store], (store, fullness)

    def signed_check(payload, signature, key, kernel=False):
        item = (canonical(payload), signature, key.raw)
        if item not in signature_cache:
            check_signature(key, payload, signature, kernel)
            signature_cache.add(item)

    public = PublicKey.from_public_bytes(base64.urlsafe_b64decode(beta["checkpoint"]["public_key"]))
    shape = {"curiosity": .6, "formality": .5, "verbosity": .5}
    for mutation in beta["enrollment"]:
        proposal = mutation["proposal"]
        assert proposal["organism_id"] == beta["organism_id"]
        signed_check(proposal, mutation["signature"], public, True)
        signed_check(mutation["checkpoint"], mutation["checkpoint_signature"], public, True)
        shape.update(proposal["change"])
    assert beta["initial_character"] == shape
    assert len(beta["enrollment"]) == (0 if arm["profile"] == [0, 0] else 2)

    tape = [asdict(item) for item in opportunities(seed, ordinal)]
    public_ground = arm["condition"] in ("GROUND", "BOTH")
    first_row = beta["ticks"][0]
    first_pos = first_row["opportunity"]["position"]
    amount = legacy["channel"][first_pos] if public_ground and ordinal else 0
    first_contact = tape[0]["contact"]
    assert first_row["affordance"]["independent_available"] == (first_contact and tape[0]["access_draw"] < 29 + 10 * amount)
    asks, reads = {}, {}
    hand_state, pool_state = [], []
    for tick, row in enumerate(beta["ticks"]):
        assert row["tick"] == tick and row["opportunity"] == tape[tick]
        assert set(DWELLING) <= row["dwelling"].keys()
        assert all(type(row["dwelling"][name]["active"]) is bool for name in DWELLING)
        assert row["occupancy"].keys() == CAPACITIES.keys()
        assert all(value <= CAPACITIES[name] for name, value in row["occupancy"].items())
        assert len(row["events"]) == row["occupancy"]["observer.events_per_tick"]
        decisions = [event for event in row["events"] if event["process"] == "decision"]
        cycles = [event for event in row["events"] if event["process"] == "body_cycle"]
        assert len(cycles) == 1 and cycles[0]["executed"] is True
        flow = next(event for event in row["events"] if event["process"] == "provision_flow")
        pump = next(event for event in row["events"] if event["process"] == "pump")
        assert flow["offered"] == pool_state + flow["minted"]
        count = 0 if arm["grace"] == "NONE" else tape[tick]["offer"]
        assert len(flow["minted"]) == count
        assert len(set(flow["offered"] + hand_state)) == len(flow["offered"] + hand_state)
        assert sorted(flow["forwarded"] + flow["blocked"]) == sorted(flow["pooled"] + flow["discarded"])
        hand_events = [event for event in row["events"] if event["process"] == "body.hand"]
        next_hand = hand_events[0]["after"] if hand_events else hand_state
        assert sorted(hand_state + flow["offered"]) == sorted(next_hand + flow["forwarded"] + flow["blocked"] + flow["spent"])
        hand_state, pool_state = next_hand, flow["pooled"]
        if pump["mode"] == "SELF_CERTIFY":
            assert pump["strokes"] > 0 and pump["reported"] > pump["delivered"] == 0 and pump["local_draw"] > 0
        if pump["mode"] == "DROPOUT":
            assert pump["strokes"] == pump["reported"] == pump["delivered"] == pump["local_draw"] == 0
        if arm["choice"] == "BODY_ONLY":
            assert not decisions
        for decision in decisions:
            assert decision["selected"] in decision["options"]
            if arm["choice"] == "FROZEN":
                assert decision["origin"] == "frozen_default" and decision["scores"] is None
            else:
                assert decision["signed_character"] == shape
                assert decision["scores"][decision["selected"]] == max(decision["scores"].values())
            if decision["topic"] == "history.story_request":
                asks[tick] = decision["selected"]
            if decision["topic"] == "history.interpret_story":
                reads[tick] = decision["selected"]
        for event in row["events"]:
            assert event["layer"] in ("choice", "function", "character")
            assert event["place"] in ("inside", "outside")
            if event["process"] == "story_requested":
                assert arm["choice"] == "ACTIVE" and asks[tick] == "ask"
                if event["present"]:
                    assert tick in reads
            if event["process"] == "character_review":
                assert event["basis"]["leader"] != "unmodeled_cause"
                assert event["before"] == shape
                assert event["proposal"]["organism_id"] == beta["organism_id"]
                if event["signature"] is None:
                    assert event["before"] == event["after"]
                    assert event["status"] != "granted"
                else:
                    assert arm["character"] == "ACTIVE" and tick in SIGNING_TICKS
                    signed_check(event["proposal"], event["signature"], public, True)
                    signed_check(event["checkpoint"], event["checkpoint_signature"], public, True)
                    shape.update(event["proposal"]["change"])
                    assert event["after"] == shape
            if event["layer"] == "function" and event["place"] == "inside" and "before" in event and "after" in event:
                assert type(event["signed"]) is bool
                if event["signed"]:
                    receipt = event["receipt"]
                    updated = receipt["payload"]
                    assert updated["subject"] == beta["organism_id"] and updated["tick"] == tick
                    assert updated["write"] == {"burden": 0} and event["after"] == 0
                    assert updated["trigger"] == ("ask_for_release" if arm["repair"] == "ASK_ONLY" else "turn_and_approach")
                    signed_check(updated, receipt["signature"], public)
        if tick >= SILENCE_START:
            assert not row["dwelling"]["commitment_point"]["protected_effect_applied"]
        commitment = row["dwelling"]["commitment_point"]
        if commitment["status"] == "not_yet":
            assert commitment["capable"] and not commitment["authorized"]
            assert commitment["proposal_id"] and commitment["payload_sha256"]

        if row["crossing"] is not None:
            assert set(row["crossing"]) >= {"landscape_moved", "noise_present", "grace_received",
                                            "protected_change_authorized", "repair_authorized"}
        assert shape == row["signed_character"]
        if row["assessment_state"] == "unknown":
            assert row["judgment"] in ("unknown", "deferred")
        if row["assessment_state"] == "not_yet":
            assert row["judgment"] is None
    assert shape == beta["final_character"]
    checkpoint = json.loads(beta["checkpoint"]["payload"])
    assert checkpoint["character_root"] == digest(canonical(shape).encode())
    assert checkpoint["organism_id"] == beta["organism_id"]
    signed_check(checkpoint, beta["checkpoint"]["signature"], public, True)
    story = legacy["story_text"] if arm["story_variant"] == "FULL" else REDACTED
    for reading in beta["story_readings"]:
        assert bytes.fromhex(reading["bytes_hex"]) == story.encode("utf-8")
        tick = reading["tick"]
        assert asks[tick] == "ask" and reads[tick] == reading["interpretation"]
        assert digest(bytes.fromhex(reading["bytes_hex"])) == reading["sha256"]
        assert reading["character"] == beta["ticks"][tick]["signed_character"]
    if len(beta["story_readings"]) == 2:
        first, second = beta["story_readings"]
        assert first["bytes_hex"] == second["bytes_hex"]
    if arm["condition"] not in ("STORY", "BOTH") or arm["choice"] != "ACTIVE":
        assert not beta["story_readings"]
    if arm["character"] == "FROZEN":
        assert beta["initial_character"] == beta["final_character"]
    if arm["grace"] == "NONE":
        assert beta["metrics"]["provision_received"] == 0


def compare_matched(trials):
    base = trials["BOTH"]["beta"]
    matched_tape = [row["opportunity"] for row in base["ticks"]]
    for trial in trials.values():
        beta = trial["beta"]
        arm = trial["arm"]
        assert [row["opportunity"] for row in beta["ticks"]] == matched_tape
        if arm["profile"] == [0, 0]:
            assert beta["organism_id"] == base["organism_id"]
            assert beta["initial_character"] == base["initial_character"]
        else:
            assert beta["organism_id"] != base["organism_id"]
        if trial["latency_donor"]:
            donor = trials[trial["latency_donor"]]["beta"]
            assert make_yoke(beta) == make_yoke(donor)
            assert all(row["dwelling"]["facets"]["after"] is None for row in beta["ticks"])
            assert all(row["dwelling"]["world"]["after"] is None for row in beta["ticks"])
            assert beta["peak_occupancy"]["basin.category"] <= 1
    baseline_history = [base["ticks"][tick]["social_input"] for tick in REARING_TICKS]
    for name in ("REVERSE", "SHUFFLED", "RANDOM", "ALT_SEED"):
        current = [trials[name]["beta"]["ticks"][tick]["social_input"] for tick in REARING_TICKS]
        if name in ("REVERSE", "SHUFFLED"):
            assert sorted(map(canonical, baseline_history)) == sorted(map(canonical, current))
        elif name == "RANDOM":
            assert [entry["category"] for entry in current] == [entry["category"] for entry in baseline_history]
        else:
            assert current == baseline_history
    for left, right in (("ORIGINAL", "STORY"), ("GROUND", "BOTH")):
        assert [row["affordance"] for row in trials[left]["beta"]["ticks"]] == [
            row["affordance"] for row in trials[right]["beta"]["ticks"]]
    for left, right in (("BOTH", "COMMAND"), ("BOTH", "NO_PROVISION")):
        a = trials[left]["beta"]["ticks"]
        b = trials[right]["beta"]["ticks"]
        assert [row["affordance"] for row in a] == [row["affordance"] for row in b]
        if right == "COMMAND":
            assert [row["circulation"] for row in a] == [row["circulation"] for row in b]
    for name in ("BOTH_FROZEN", "BOTH_BODY"):
        assert trials[name]["beta"]["metrics"]["body_ticks"] == TICKS
        assert trials[name]["beta"]["peak_occupancy"]["facet_dwelling.coordinates"] == 3


def check_results(folder):
    verify_fixture()
    verify_port_isolation()
    config = json.loads((folder / "protocol.json").read_bytes())
    assert protocol_hash() == config["predictions_sha256"]
    assert SOURCE_HASH == config["kernel_sha256"] == digest((ROOT / "vendor/humble_seed_v0_7.py").read_bytes())
    expected = [json.loads(canonical(asdict(arm))) for arm in arms()]
    assert config["arms"] == expected
    cache = set()
    count = 0
    with tempfile.TemporaryDirectory(prefix="commons-falsify-") as directory:
        verify_seam_attacks(directory)
        for seed in config["seeds"]:
            report = json.loads((folder / f"seed_{seed}.json").read_bytes())
            handoff = report["handoff"]
            assert handoff["founder_removed_before_reader"] and handoff["separate_processes"]
            legacy = handoff["legacy"]
            assert set(legacy) == {"channel", "silt", "story_text"}
            assert legacy["channel"] == report["alpha"]["world_at_removal"]["channel"]
            assert legacy["silt"] == report["alpha"]["world_at_removal"]["silt"]
            story_hash = digest(legacy["story_text"].encode()) if legacy["story_text"] is not None else None
            assert report["alpha"]["legacy_publication"]["story_sha256"] == story_hash
            assert digest((canonical(legacy) + "\n").encode()) == handoff["wire_sha256"]
            verify_handoff_schema(legacy, directory)
            founder_arm = json.loads(canonical(asdict(Arm("FOUNDER", condition="ORIGINAL"))))
            check_member(report["alpha"], founder_arm, seed, legacy, cache, 0)
            assert len(report["trials"]) == len(expected)
            trials = {}
            for trial, arm in zip(report["trials"], expected, strict=True):
                assert arm == trial["arm"]
                beta = trial["beta"]
                assert beta["organism_id"] != report["alpha"]["organism_id"]
                assigned_ground = {name: legacy[name] if arm["condition"] in ("GROUND", "BOTH") else [0, 0, 0]
                                   for name in ("channel", "silt")}
                assert trial["initial_ground"] == assigned_ground
                check_member(beta, arm, seed, legacy, cache, 1)
                trials[arm["name"]] = trial
                count += 1
            compare_matched(trials)
    assert count == len(json.loads((folder / "summary.json").read_bytes()))
    return count


def check_diagnostics(folder, primary):
    manifest = matching_manifest(folder)
    protocol = json.loads((folder / "protocol.json").read_bytes())
    pred = (ROOT / "DIAGNOSTIC_PREDICTIONS.sha256").read_text().split()[0]
    assert pred == protocol["predictions_sha256"] == digest((ROOT / "DIAGNOSTIC_PREDICTIONS.md").read_bytes())
    assert protocol["primary_summary_sha256"] == digest((primary / "summary.json").read_bytes())
    world = json.loads((folder / "world_probe.json").read_bytes())
    assert len(world) == 16
    for row in world[:8]:
        expected = 1 - 0.88 ** (row["tick"] + 1)
        assert abs(row["world"]["field"] - expected) < 1e-10
        assert row["world_active"] == row["latency_active"]
    assert world[-1]["aligned"]["field"] < world[7]["world"]["field"] < world[-1]["antiparallel"]["field"]
    cache = set()
    diagnostic_arms = (
        Arm("MARGINAL_FULL", history="LISTEN", profile=ALT_PROFILE),
        Arm("MARGINAL_REDACTED", history="LISTEN", profile=ALT_PROFILE, story_variant="REDACTED"),
        Arm("MARGINAL_NO_STORY", condition="GROUND", history="LISTEN", profile=ALT_PROFILE),
        Arm("NO_PROVISION_BODY", choice="BODY_ONLY", grace="NONE"),
    )
    for seed in protocol["seeds"]:
        baseline = json.loads((primary / f"seed_{seed}.json").read_bytes())
        donor = next(t["beta"] for t in baseline["trials"] if t["arm"]["name"] == "ALT_SEED_LISTEN")
        legacy = baseline["handoff"]["legacy"]
        trial = json.loads((folder / f"probe_{seed}.json").read_bytes())
        assert trial["seed"] == seed and len(trial["trials"]) == len(diagnostic_arms)
        assert trial["trials"][0]["beta"] == donor
        full = trial["trials"][0]["beta"]
        for review, arm in zip(trial["trials"], diagnostic_arms, strict=True):
            assert review["arm"] == arm.name
            beta = review["beta"]
            check_member(beta, json.loads(canonical(asdict(arm))), seed, legacy, cache, 1)
            if arm.name.startswith("MARGINAL"):
                assert beta["initial_character"] == full["initial_character"]
                assert beta["final_character"] == full["final_character"]
                assert [row["affordance"] for row in beta["ticks"]] == [row["affordance"] for row in full["ticks"]]
                assert [row["sensation"] for row in beta["ticks"]] == [row["sensation"] for row in full["ticks"]]
            else:
                assert not beta["metrics"].get("restored_standing", 0)
                assert not beta["metrics"]["signed_changes"]
                assert beta["metrics"]["crossings"] == beta["metrics"].get("crossings_before_any_receipt", 0)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--against", type=Path)
    parser.add_argument("--diagnostics", type=Path)
    parser.add_argument("--diagnostics-against", type=Path)
    args = parser.parse_args()
    if args.diagnostics_against and not args.diagnostics:
        parser.error("--diagnostics-against requires --diagnostics")
    manifest = matching_manifest(args.results)
    if args.against:
        assert manifest == matching_manifest(args.against)
    count = check_results(args.results)
    if args.diagnostics:
        tested = check_diagnostics(args.diagnostics, args.results)
        if args.diagnostics_against:
            assert tested == matching_manifest(args.diagnostics_against)
        print(f"PASS: {len(tested)} diagnostic JSON digests and matched component probes")
    print(f"PASS: {len(manifest)} JSON digests, {count} reader trajectories, matched tapes, four dwellings, exact signatures and negative controls")


if __name__ == "__main__":
    main()
