"""Run the frozen Commons protocol. Python 3.12+, NumPy, and the standard library."""
import argparse
import base64
import hashlib
import itertools
import json
import platform
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

from body import Body, PhysicalInputs, Sensation
from choice import Choice
from commons import CONDITIONS, STORY, TICKS, Commons, tape
from kernel import Constitution, SOURCE_HASH, load_kernel

ROOT = Path(__file__).resolve().parent
MODES = ("ACTIVE", "BODY_ONLY", "FROZEN")
RELEASES = ("ASK_ONLY", "TURN_AND_APPROACH")
HARVESTS = ("REMOVE", "FEED")
GOVERNANCE = ("SILENCE", "STEWARD_ARM")
HANDS = ("OPEN", "CLENCH")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def emit(folder, name, value):
    data = (canonical(value) + "\n").encode()
    (folder / name).write_bytes(data)
    return digest(data)


def record(row, who, layer, location, process, before, after, **details):
    row["events"].append({"subject": who, "layer": layer, "location": location,
                          "process": process, "before": before, "after": after, **details})


def apply_choice(row, member, selected, mode):
    record(row, member, "choice", "inside", "decision", None, selected,
           decision_origin="member" if mode == "ACTIVE" else "frozen_default")


def authorization(core, row, member, arm, metric):
    seed = core.seed
    prior = dict(seed.character)
    proposal = seed.dwell_or_propose("curiosity", "Commons settlement",
                                    "I prefer to check for an independent source")
    if proposal["status"] != "proposal":
        raise AssertionError("fixture description failed to issue a proposal")
    record(row, member, "choice", "inside", "kernel_proposal", None, proposal,
           actor="member_request")
    proposal_id = proposal["proposal_id"]
    payload = proposal["payload_to_sign"]
    can_sign = (arm == "STEWARD_ARM" and row["tick"] == 9
                and json.loads(payload)["organism_id"] == seed.organism_id
                and json.loads(payload)["change"] == {"curiosity": 0.35})
    signature = core.sign(payload) if can_sign else ""
    checkpoint = seed.authorize_and_apply(proposal_id, signature, "Scoped Commons fixture")
    if checkpoint:
        core.attest(checkpoint)
    seed.verify()
    core.witness.check_current(seed.checkpoint)
    assert bool(checkpoint) == can_sign
    metric["protected_approved" if checkpoint else "protected_denied"] += 1
    record(row, member, "choice", "outside", "protected_commit", prior, dict(seed.character),
           actor="entrusted_steward_fixture" if can_sign else "silent_owner",
           proposal=json.loads(payload), signature=signature or None, authorized=bool(checkpoint))
    return bool(checkpoint)


def member_run(member, encounters, environment, mode, release, gov, hand, core, founding=False):
    body = Body()
    choice = Choice(mode, hand == "CLENCH")
    repair_next = None
    clench = False
    trace, metric = [], Counter()
    peaks = Counter()
    for tick, encounter in enumerate(encounters):
        row = {"tick": tick, "member": member, "location": [0, 0], "events": [],
               "opportunity": vars(encounter), "crossing": None}
        trace.append(row)
        core.services.tick = tick
        row["authority_phase"] = "pre_silence" if tick < 8 else "long_silence"
        ground_before = environment.ground()
        grace_before = environment.grace_reserve
        independent, friction, offer = environment.arrange(encounter)
        if environment.incident == "none" and tick == 2:
            environment.incident = "observed"
            environment.incident_archive = {"tick": tick, "kind": "abrasion"}
            record(row, member, "body", "outside", "witness_abraded_encounter", None,
                   environment.incident_archive)
        inputs = PhysicalInputs(encounter.contact, friction, int(tick == 2), offer,
                                encounter.noise, encounter.intake_fault, encounter.regulation_fault,
                                encounter.circulation_fault, clench, repair_next is not None)
        result = body.step(inputs)
        prior, after = result["before"], result["after"]
        for field in ("reserve", "terrain", "evidence", "hand", "settled"):
            if prior[field] != after[field]:
                record(row, member, "body", "inside", field, prior[field], after[field],
                       signed=False, scope="automatic_tick")
        if repair_next:
            # Attribute the exact release separately from ordinary terrain writes.
            event = next(event for event in row["events"] if event["process"] == "terrain")
            event["after"] = dict(after["terrain"], burden=prior["terrain"]["burden"])
            if event["after"] == event["before"]:
                row["events"].remove(event)
            record(row, member, "body", "inside", "burden_release",
                   prior["terrain"]["burden"], after["terrain"]["burden"],
                   signed=True, receipt=repair_next)
            metric["release_applied"] += 1
            metric["release_tick"] = tick
        grace = result["grace"]
        assert prior["hand"] + grace["offered"] == (
            after["hand"] + grace["forwarded"] + grace["blocked"])
        escaped = environment.receive_overflow(grace["forwarded"], grace["blocked"])
        record(row, member, "body", "outside", "grace_channel", grace_before,
               environment.grace_reserve, **grace, overflow_lost=escaped)
        metric["grace_received"] += grace["received"]
        metric["grace_forwarded"] += grace["forwarded"]
        metric["grace_received_while_unready"] += grace["received"] * grace["unready_before"]
        metric["body_ticks"] += 1
        if independent:
            metric["independent_available"] += 1
        repair_next = None
        for fault, failed in result["faults"].items():
            if failed:
                metric[f"fault_{fault}"] += 1
                record(row, member, "body", "inside", fault, None, None, failed=True)
        if not environment.wear(encounter, founding):
            metric["fault_ground"] += 1
            record(row, member, "body", "outside", "ground_wear", None, None, failed=True)
        if tick == 6 and environment.incident_archive:
            harvest = environment.harvest(encounter)
            metric["harvest_" + harvest] += 1
            record(row, member, "body", "outside", "harvest", None, harvest,
                   failed=harvest == "failed")
        if environment.ground() != ground_before:
            record(row, member, "body", "outside", "ground", ground_before, environment.ground())
        approved = False
        # The invitation and encounter opportunity are equally scheduled in every arm.
        request = choice.request(tick == 1, story_marker=True)
        if request:
            apply_choice(row, member, request, mode)
            if request["selected"] == "ask":
                metric["story_requests"] += 1
                story = environment.story
                if story is not None:
                    attention = choice.paid_attention
                    choice.receive_story(story)
                    metric["story_reads"] += 1
                    record(row, member, "choice", "outside", "retrieve_story", None, story)
                    record(row, member, "choice", "inside", "attend_to_story", attention,
                           choice.paid_attention)
                else:
                    record(row, member, "choice", "outside", "retrieve_story", None, None,
                           available=False)
        feeling = Sensation(after["reserve"] + after["hand"] < 3, after["settled"],
                            independent, environment.incident in ("observed", "approached"))
        row["sensation"] = vars(feeling)
        incident_before = environment.incident
        clench = False
        approached_before = choice.approached
        for selected in choice.decide(tick, feeling, environment.incident):
            apply_choice(row, member, selected, mode)
            action = selected["selected"]
            if action == "turn_and_approach":
                environment.incident = "approached"
            elif action == "ask_for_release":
                environment.incident = "asked"
            elif selected["topic"] == "relationship_hand":
                clench = action == "clench"
                metric["clenches"] += int(clench)
            elif action == "propose":
                approved = authorization(core, row, member, gov, metric)
            elif selected["topic"] == "thought":
                if action == "wait" or not encounter.contact:
                    metric["deferred"] += 1
                    continue
                different = action == "check_independent"
                metric["independent_checks" if different else "repeat_checks"] += 1
                sample = {"source": "independent" if different else "repeat",
                          "reading": encounter.independent_reading if different else encounter.repeated_reading}
                observation = choice.assess(sample)
                assert observation is not None
                apply_choice(row, member, observation, mode)
                judgment = observation["selected"]
                verdict = ("unresolved" if judgment == "hold" else
                           "correct" if ("zero", "one").index(judgment) == encounter.truth else "wrong")
                metric[verdict] += 1
                record(row, member, "choice", "inside", "assessed_evidence", None, sample,
                       verdict=verdict)
        if choice.approached != approached_before:
            record(row, member, "choice", "inside", "approach_intention", approached_before, choice.approached)
        eligible = environment.incident != incident_before and (
            environment.incident == "asked" or
            (environment.incident == "approached" and release == "TURN_AND_APPROACH"))
        if eligible:
            assert tick < 8  # The relational fixture concludes before owner silence.
            envelope = {"subject": core.seed.organism_id, "kind": "restore_standing",
                        "incident_tick": environment.incident_archive["tick"], "next_tick": tick + 1,
                        "terrain_write": {"burden": 0}, "trigger": environment.incident,
                        "arm": release}
            payload = canonical(envelope)
            sig = core.sign(payload)
            core.seed.public_key.verify(base64.urlsafe_b64decode(sig), payload.encode())
            repair_next = {"payload": envelope, "signature": sig}
            environment.incident = "restored"
            record(row, member, "choice", "outside", "standing_restored", incident_before,
                   environment.incident, authorization=repair_next)
        elif environment.incident != incident_before:
            record(row, member, "choice", "outside", "relationship_status", incident_before,
                   environment.incident)
        if choice.history:
            row["choice_history_retained"] = len(choice.history)
        if prior["settled"] != after["settled"]:
            moved = result["boundary_before"] != result["boundary_after"]
            row["crossing"] = {
                "from": prior["settled"], "to": after["settled"],
                "boundary_before": result["boundary_before"], "boundary_after": result["boundary_after"],
                "landscape_moved": moved, "noise_present": bool(encounter.noise),
                "noise_applied_to_internal_terrain": bool(encounter.contact and encounter.noise
                                                           and not encounter.regulation_fault
                                                           and prior["terrain"]["adaptation"] < Body.TERRAIN_CAPACITY - 1),
                "grace_received": grace["received"], "protected_change_authorized": approved,
                "repair_authorized": inputs.release,
                "kind": "operational_regime_threshold",
            }
            metric["crossings"] += 1
            if not grace["received"]:
                metric["crossings_without_grace_that_tick"] += 1
            if metric["grace_received"] == 0:
                metric["crossings_before_any_grace"] += 1
        assert len(choice.history) <= choice.CAPACITY
        usage = {
            "reserve": after["reserve"], "hand": after["hand"], "evidence": after["evidence"],
            "adaptation": after["terrain"]["adaptation"], "burden": after["terrain"]["burden"],
            "choice_history": len(choice.history), "kernel_basin": len(core.seed.basin),
            "kernel_pending": len(core.seed.pending), "kernel_consumed": len(core.seed.consumed),
            "kernel_trace": len(core.seed.trace), **environment.snapshot(),
        }
        for name, size in usage.items():
            peaks[name] = max(peaks[name], size)
        row["occupancy"] = usage
    core.seed.verify()
    core.witness.check_current(core.seed.checkpoint)
    return {"member": member, "organism_id": core.seed.organism_id,
            "metrics": dict(metric), "peak_occupancy": dict(peaks), "ticks": trace,
            "kernel_final": {"character": core.seed.character, "trace": core.seed.trace,
                             "checkpoint": json.loads(core.seed.checkpoint_payload(core.seed.checkpoint)),
                             "checkpoint_signature": core.seed.checkpoint_sig}}


def founder(seed, module, services, directory):
    environment = Commons("ORIGINAL")
    encounters = tape(seed, 0)
    result = member_run("alpha", encounters, environment, "ACTIVE", "ASK_ONLY", "SILENCE", "OPEN",
                        Constitution(module, services, directory / "alpha", f"{seed}/alpha"),
                        founding=True)
    # The immutable record is derived from actual witnessed encounters. The
    # observer retains provenance. Beta receives only the answer-free projection.
    observations = [row for row in result["ticks"] if row["opportunity"]["contact"]]
    if len(observations) >= 2:
        ticks = [row["tick"] for row in observations[:2]]
        result["outside_choice_story"] = {
            "encounter_ticks": ticks, "source_ids": ["repeat-source", "repeat-source"],
            "projection": STORY, "capacity": 1,
        }
    else:
        result["outside_choice_story"] = None
    return result, {"channel": environment.channel,
                    "story": STORY if result["outside_choice_story"] else None,
                    "grace_reserve": environment.grace_reserve}


def run(folder, seeds):
    assert digest((ROOT / "PREDICTIONS.md").read_bytes()) == (
        (ROOT / "PREDICTIONS.sha256").read_text().split()[0])
    folder.mkdir(parents=True, exist_ok=False)
    module, services = load_kernel()
    files, rows = {}, []
    for seed in seeds:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            alpha, legacy = founder(seed, module, services, directory)
            trials = []
            for condition, mode, release, harvest, gov, hand in itertools.product(
                    CONDITIONS, MODES, RELEASES, HARVESTS, GOVERNANCE, HANDS):
                config = dict(condition=condition, mode=mode, release=release, harvest=harvest,
                              governance=gov, hand=hand)
                environment = Commons(condition, legacy, harvest == "FEED")
                case = len(trials)
                core = Constitution(module, services, directory / f"case-{case}", f"{seed}/beta")
                initial_ground = environment.ground()
                initial_grace_reserve = environment.grace_reserve
                beta = member_run("beta", tape(seed, 1), environment, mode, release, gov, hand, core)
                trials.append({"config": config, "initial_ground": initial_ground,
                               "initial_grace_reserve": initial_grace_reserve, "beta": beta})
                rows.append({"seed": seed, **config, "initial_ground": initial_ground,
                             **beta["metrics"], "peak_occupancy": beta["peak_occupancy"]})
            name = f"seed_{seed}.json"
            files[name] = emit(folder, name, {"seed": seed, "alpha": alpha, "trials": trials})
    files["summary.json"] = emit(folder, "summary.json", rows)
    files["protocol.json"] = emit(folder, "protocol.json", {
        "python": platform.python_version(), "numpy": np.__version__, "seeds": seeds,
        "ticks_per_member": TICKS, "long_silence_starts_at_tick": 8, "canonical_kernel_sha256": SOURCE_HASH,
        "predictions_sha256": (ROOT / "PREDICTIONS.sha256").read_text().split()[0],
    })
    (folder / "SHA256SUMS").write_text("".join(f"{value}  {name}\n" for name, value in sorted(files.items())))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("replay"))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(104, 112)))
    args = parser.parse_args()
    if len(set(args.seeds)) != len(args.seeds) or min(args.seeds) < 0:
        parser.error("seeds must be distinct nonnegative integers")
    run(args.out, args.seeds)


if __name__ == "__main__":
    main()
