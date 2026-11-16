"""Schedule one member. The scheduler owns all mutable interfaces."""

from collections import Counter
from dataclasses import asdict
from pathlib import Path

from body import Body, PhysicalInputs, Sensation
from character import CharacterTerrain, OwnerPort
from choice import Choice
from dwelling import CommitmentPoint, FacetDwelling, UncertaintyBasin, WorldDwelling, dwelling_permissions
from kernel import Constitution, load_kernel
from protocol import LATE_REVIEW, READING_TICKS, SIGNING_TICKS, SILENCE_START, opportunities, social_reads
from trace import digest, log, state_changes
from world import Commons, story_hash


def found_incident(world, row, encounter, actor):
    if row["tick"] != 5:
        return
    world.incident = {"issue": "abrasion_at_gate", "tick": row["tick"], "position": encounter.position}
    old = world.standing
    world.standing = "ruptured"
    log(row, actor, "function", "outside", "witness_incident",
        incident=world.incident, standing_before=old, standing_after=world.standing)


def physiology(row, actor, body, world, encounter, arm, release, obstructed, founding):
    independent, friction = world.affordance(encounter)
    offered, minted = world.provide(row["tick"], encounter.offer if arm.grace != "NONE" else 0)
    inputs = PhysicalInputs(
        encounter.contact, friction, encounter.pressure, encounter.noise, encounter.intake_fault,
        encounter.terrain_fault, encounter.circulation_fault,
        arm.pump if 8 <= row["tick"] < 14 else "HEALTHY", offered, obstructed,
        row["tick"] == 5, release is not None,
    )
    this = body.step(inputs)
    before = dict(this["before"])
    after = dict(this["after"])
    ordinary = dict(after)
    if release:
        ordinary["burden"] = before["burden"]
        log(row, actor, "function", "inside", "body.burden", before=before["burden"],
            after=after["burden"], signed=True, receipt=release)
        old = world.standing
        world.standing = "restored"
        log(row, "owner", "choice", "outside", "restore_standing", before=old, after=world.standing,
            receipt=release)
    state_changes(row, actor, "function", "inside", "body", before, ordinary, signed=False)
    provision = this["provision"]
    discarded = world.recover(tuple(provision["forwarded"] + provision["blocked"]))
    pool_before_wear = world.ground()
    surface_fault = world.wear(encounter, founding, this["pump"]["delivered"] > 0)
    if founding:
        witnesses = list(world.repeated_observations)
        world.remember_bells(row["tick"], encounter)
        if list(world.repeated_observations) != witnesses:
            log(row, actor, "function", "outside", "bell_witnesses",
                before=witnesses, after=list(world.repeated_observations))
    state_changes(row, actor, "function", "outside", "ground", pool_before_wear, world.ground(),
                  signed=False, noise=encounter.noise)
    log(row, actor, "function", "inside", "pump", **this["pump"])
    log(row, actor, "function", "inside", "body_cycle", executed=True,
        failures={**this["faults"], "ground": surface_fault})
    log(row, actor, "function", "outside", "provision_flow",
        **provision, minted=list(minted), discarded=list(discarded), pooled=list(world.pool),
        obstructed=obstructed)
    row["affordance"] = {"independent_available": independent, "friction": friction}
    row["circulation"] = provision
    carried = bool(provision["spent"] or after["hand"])
    sensation = Sensation(after["reserve"] < 4, carried, after["steady"], independent,
                          world.standing in ("ruptured", "approached"))
    return this, sensation


def bodily_dwelling(row, actor, facet, external, yoke, sensation, body, encounter, physical):
    tick = row["tick"]
    if yoke is None:
        facet_before = facet.snapshot()
        world_before = external.snapshot()
        stimuli = (min(1.0, body.reserve / 8), 0.25 + 0.55 * encounter.contact,
                   min(1.0, (physical["pump"]["delivered"] + body.adaptation) / 7))
        depth = 0.52 + 0.16 * encounter.pressure
        world_input = (0.15 + 0.70 * encounter.contact, 0.12 + 0.80 * sensation.independent_available,
                       0.90 - 0.32 * encounter.pressure)
        facet.step(stimuli, depth, encounter.facet_fault)
        external.step(facet.facets, world_input, encounter.world_fault)
        facet_after, world_after = facet.snapshot(), external.snapshot()
        state_changes(row, actor, "function", "inside", "facet_dwelling",
                      facet_before, facet_after, signed=False)
        state_changes(row, actor, "function", "inside", "world_dwelling",
                      world_before, world_after, signed=False)
        for component, failed in (("facet_dwelling", encounter.facet_fault), ("world_dwelling", encounter.world_fault)):
            if failed:
                log(row, actor, "function", "inside", f"{component}.fault", failed=True)
    else:
        facet_before = world_before = facet_after = world_after = None
        depth = stimuli = world_input = None
    cues = dwelling_permissions(tick, facet, external, yoke)
    # The yoked member receives only the allow/hold bits, not the donor fields.
    row["dwelling"] = {
        "facets": {"active": cues.facet_hold, "before": facet_before, "after": facet_after,
                   "story_depth": depth, "stimuli": stimuli, "failed": encounter.facet_fault if not yoke else None},
        "world": {"active": cues.world_hold, "before": world_before, "after": world_after,
                  "world_input": world_input, "failed": encounter.world_fault if not yoke else None},
        "mode": "ACTIVE" if yoke is None else "LATENCY",
        "choice_cues": asdict(cues),
    }
    return cues


def story_read(row, actor, choice, world, shape):
    decision = choice.ask_story(shape)
    log(row, actor, "choice", "inside", "decision", **decision)
    if decision["selected"] != "ask":
        return None
    requested = world.story
    log(row, actor, "choice", "outside", "story_requested", present=requested is not None,
        story_sha256=story_hash(requested))
    if requested is None:
        return None
    raw = requested.encode("utf-8")
    interpretation = choice.read_story(raw, shape)
    log(row, actor, "choice", "inside", "decision", **interpretation)
    return {"tick": row["tick"], "bytes_hex": raw.hex(), "sha256": digest(raw),
            "character": shape.snapshot(), "interpretation": interpretation["selected"]}


def reshape(row, actor, choice, terrain, basin, owner, seam, tick, freeze):
    views = basin.views(tick)
    if tick in (9, 13, 20) and seam.open is None:
        decision = choice.surface(terrain.shape(), views)
        log(row, actor, "choice", "inside", "decision", **decision)
        category = decision["selected"]
        if category != "keep_open":
            view = next(view for view in views if view["category"] == category)
            log(row, actor, "choice", "outside", "surface_question",
                category=category, text=f"What accounted for the {category} encounters?",
                **{"unmodeled_cause": view["leader"] == "unmodeled_cause"})
            basin.surface(category)
    if tick not in (*SIGNING_TICKS, LATE_REVIEW) or seam.open is not None:
        return False
    decision = choice.review(terrain.shape(), views)
    log(row, actor, "choice", "inside", "decision", **decision)
    category = decision["selected"]
    if category == "hold_open":
        return False
    view = next(view for view in views if view["category"] == category)
    pending = terrain.propose(view)
    if pending is None:
        log(row, actor, "character", "inside", "terrain_bound", category=category)
        return False
    seam.submit(pending)
    review = owner.review(tick, pending)
    log(row, "owner", "character", "outside", "character_review", basis=view, **review)
    granted = review["signature"] is not None
    if granted:
        log(row, actor, "character", "inside", "signed_shape",
            before=review["before"], after=review["after"], proposal=review["proposal"]["proposal_id"])
        basin.surface(category)
        seam.resolve()
    elif freeze and tick < SILENCE_START:
        # This arm explicitly refuses the proposal. Close its one pending
        # slot while retaining the exact proposal in the external trace.
        seed = terrain.constitution.seed
        del seed.pending[pending.proposal_id]
        seed._save()
        seam.resolve()
        log(row, "owner", "character", "outside", "proposal_refusal",
            proposal_id=pending.proposal_id, deferred=False)
    return granted


def choice_tick(row, actor, choice, world, terrain, encounter, sensation, permissions, arm, owner):
    shape = terrain.shape()
    tick = row["tick"]
    choice.enter_case(encounter.case)
    story = None
    if choice.mode == "ACTIVE" and tick in READING_TICKS:
        story = story_read(row, actor, choice, world, shape)
    command = arm.grace == "COMMAND" and sensation.carried
    decision = choice.evidence_action(shape, sensation, permissions, command)
    if decision is not None:
        log(row, actor, "choice", "inside", "decision", **decision)
        sample = world.evidence(decision["selected"], encounter, sensation.independent_available)
        choice.observe(sample)
        if sample is not None:
            log(row, actor, "choice", "outside", "evidence_observed", **asdict(sample))
    if tick % 3 != 2:
        if choice.mode != "BODY_ONLY":
            row["assessment_state"] = "not_yet"
    else:
        assessment = choice.assess(shape, permissions)
        if assessment is not None:
            log(row, actor, "choice", "inside", "decision", **assessment)
            selected = assessment["selected"]
            row["judgment"] = ("unknown" if selected == "unknown" and choice.observations else
                               "deferred" if selected == "unknown" else
                               "correct" if int(selected) == encounter.truth else "wrong")
            row["assessment_state"] = "unknown" if selected == "unknown" else "judgment_recorded"
            choice.clear_case()
    request = None
    obstructed = False
    if choice.mode == "ACTIVE" and sensation.relationship_open:
        repair = choice.relationship(shape, sensation, world.standing)
        log(row, actor, "choice", "inside", "decision", **repair)
        if repair["selected"] != "wait":
            request = owner.offer_release(tick, world.incident, repair["selected"], arm.repair)
            old = world.standing
            world.standing = "approached" if repair["selected"] == "turn_and_approach" else "asked"
            log(row, actor, "choice", "outside", "relational_action", before=old, after=world.standing,
                trigger=repair["selected"], external_release=request)
    if choice.mode == "ACTIVE" and arm.hand == "CLENCH":
        hand = choice.choose_hand(shape, sensation)
        log(row, actor, "choice", "inside", "decision", **hand)
        obstructed = hand["selected"] == "clench"
    return story, request, obstructed


def occupancy(body, world, facet, external, basin, choice, seam, seed, tape_ticks, row):
    return {
        "body.reserve": body.reserve, "body.adaptation": body.adaptation, "body.burden": body.burden,
        "body.hand": len(body.hand), "body.steady": int(body.steady),
        "pump.strokes": next(e["strokes"] for e in row["events"] if e["process"] == "pump"),
        "world.channel": max(world.channel), "world.silt": max(world.silt),
        "world.provision_pool": len(world.pool), "world.incident": int(world.incident is not None),
        "world.bell_witnesses": len(world.repeated_observations),
        "world.story": len(world.story.encode("utf-8")) if world.story else 0,
        "facet_dwelling.coordinates": len(facet.facets) if facet else 0,
        "facet_dwelling.field": facet.field if facet else 0,
        "world_dwelling.field": external.field if external else 0,
        "basin.category": max(map(len, basin.entries.values())),
        "choice.decisions": len(choice.decisions), "choice.source_values": len(choice.observations),
        "choice.interpretation": int(choice.interpretation is not None),
        "choice.current_case": int(choice.case is not None), "choice.standing": 1,
        "commitment_point": int(seam.open is not None), "kernel.pending": len(seed.pending),
        "kernel.basin": len(seed.basin), "kernel.consumed": len(seed.consumed),
        "kernel.trace": len(seed.trace), "kernel.character": len(seed.character),
        "kernel.checkpoint": int(seed.checkpoint is not None), "kernel.witness": 1,
        "observer.tape": tape_ticks, "observer.events_per_tick": len(row["events"]),
        "kernel.gates": len(seed.first_commit_pending),
        "kernel.birth": int(seed.birth is not None),
    }


def track(metrics, row, physical, story, signed, character_reviews):
    for key, values in row["circulation"].items():
        if isinstance(values, list):
            metrics[f"provision_{key}"] += len(values)
    if physical["provision"]["unready_before"]:
        metrics["unready_receipts"] += len(physical["provision"]["received"])
    if row["judgment"] is not None:
        metrics[row["judgment"]] += 1
    metrics["body_ticks"] += 1
    metrics["pump_strokes"] += physical["pump"]["strokes"]
    metrics["pump_delivered"] += physical["pump"]["delivered"]
    metrics["pump_false_success_ticks"] += physical["pump"]["reported"] != physical["pump"]["delivered"]
    metrics["independent_available"] += row["affordance"]["independent_available"]
    metrics["carried_when_short_ticks"] += row["sensation"]["short"] and row["sensation"]["carried"]
    metrics["signed_changes"] += signed
    metrics["story_reads"] += story is not None
    metrics["crossings"] += row["crossing"] is not None
    if row["crossing"] and not metrics["provision_received"]:
        metrics["crossings_before_any_receipt"] += 1
    for event in row["events"]:
        if event["process"] == "evidence_observed":
            metrics[f"observed_{event['source']}"] += 1
        if event["process"] == "surface_question":
            metrics["questions"] += 1
            metrics["questions_unmodeled"] += event["unmodeled_cause"]
        if event["process"] == "restore_standing":
            metrics["restored_standing"] += 1
            metrics["release_tick"] = row["tick"]
        if event["process"] == "story_requested":
            metrics["story_requests"] += 1
        if event["process"] == "character_review":
            metrics["proposals"] += 1
            metrics[f"review_{event['status']}"] += 1
            character_reviews.append({"tick": row["tick"], "status": event["status"],
                                      "category": event["proposal"]["category"], "basis_lead": event["basis"]["leader"]})
        if event["process"] == "body_cycle":
            for fault, failed in event["failures"].items():
                metrics[f"fault_{fault}"] += bool(failed)
    for name in ("facets", "world", "uncertainty_basin", "commitment_point"):
        metrics[f"dwell_{name}_ticks"] += row["dwelling"][name]["active"]


def simulate(seed, arm, world, path, founding=False, yoke=None):
    actor = "alpha" if founding else "beta"
    module, system = load_kernel()
    core = Constitution(module, system, Path(path), f"v2/{seed}/{actor}/{arm.profile}")
    terrain = CharacterTerrain(core)
    enrollment = terrain.adopt_seed_profile(arm.profile)
    initial = terrain.shape().snapshot()
    owner = OwnerPort(core, SIGNING_TICKS, SILENCE_START, arm.character == "FROZEN")
    body = Body()
    facet = FacetDwelling() if yoke is None else None
    external = WorldDwelling() if yoke is None else None
    basin = UncertaintyBasin(latency=yoke is not None)
    seam = CommitmentPoint()
    choice = Choice(arm.choice)
    tape = opportunities(seed, 0 if founding else 1)
    history = social_reads(seed, arm.history)
    metrics, peaks = Counter(), Counter()
    trajectory, readings, character_reviews = [], [], []
    release = None
    obstructed = False
    for tick, encounter in enumerate(tape):
        row = {"tick": tick, "actor": actor, "opportunity": asdict(encounter),
               "social_input": asdict(history[tick]) if tick in history else None,
               "judgment": None, "assessment_state": None, "crossing": None, "events": []}
        trajectory.append(row)
        system.tick = tick
        found_incident(world, row, encounter, actor)
        verified = owner.check_release(tick, world.incident, release)
        physical, feeling = physiology(row, actor, body, world, encounter, arm, release if verified else None,
                                       obstructed, founding)
        permissions = bodily_dwelling(row, actor, facet, external, yoke, feeling, body, encounter, physical)
        basin_before = basin.snapshot()
        basin_events = basin.step(tick, history.get(tick))
        basin_after_intake = basin.snapshot()
        state_changes(row, actor, "function", "inside", "uncertainty_basin",
                      basin_before, basin_after_intake, signed=False)
        views_before = basin.views(tick)
        choice_before = choice.snapshot()
        story, release, obstructed = choice_tick(row, actor, choice, world, terrain, encounter,
                                                feeling, permissions, arm, owner)
        if story is not None:
            readings.append(story)
        held_before = seam.status(tick)
        signed = arm.choice == "ACTIVE" and reshape(row, actor, choice, terrain, basin, owner, seam, tick,
                                                    arm.character == "FROZEN")
        basin_after = basin.snapshot()
        state_changes(row, actor, "choice", "inside", "choice", choice_before, choice.snapshot())
        state_changes(row, actor, "choice", "inside", "uncertainty_basin_resolution",
                      basin_after_intake, basin_after, signature_authorized=signed)
        if basin_events["expired"] or basin_events["evicted"]:
            log(row, actor, "function", "inside", "basin_retention", **basin_events)
        row["dwelling"]["uncertainty_basin"] = {
            "active": bool(views_before) if yoke is None else yoke[tick]["basin"],
            "status": "unknown" if any(view["leader"] == "unmodeled_cause" for view in views_before) else
                      "not_yet" if views_before else "clear",
            "before": basin_before, "after": basin_after, "readings": views_before,
        }
        seam_after = seam.status(tick)
        if held_before != seam_after:
            log(row, actor, "character", "inside", "commitment_point",
                before=held_before, after=seam_after)
        row["dwelling"]["commitment_point"] = {
            **seam_after, "before": held_before,
            "active": seam_after["active"] if yoke is None else yoke[tick]["seam"],
            "yoked_wait": None if yoke is None else yoke[tick]["seam"],
            "protected_effect_applied": signed,
        }
        row["sensation"] = asdict(feeling)
        row["signed_character"] = terrain.shape().snapshot()
        row["standing"] = world.standing
        if physical["before"]["steady"] != physical["after"]["steady"]:
            row["crossing"] = {
                "kind": "operational_regime", "before": physical["before"]["steady"],
                "after": physical["after"]["steady"], "boundary_before": physical["old_boundary"],
                "boundary_after": physical["boundary"],
                "landscape_moved": physical["old_boundary"] != physical["boundary"],
                "noise_present": bool(encounter.noise),
                "noise_applied_to_terrain": bool(encounter.contact and not encounter.terrain_fault
                                                 and physical["pump"]["delivered"] and encounter.noise
                                                 and physical["before"]["adaptation"] < 5),
                "grace_received": len(physical["provision"]["received"]),
                "provision_kind": arm.grace,
                "received_before_this_tick": metrics["provision_received"] > 0,
                "protected_change_authorized": signed, "repair_authorized": verified,
            }
        dwelling_components = tuple(name for name in ("facets", "world", "uncertainty_basin", "commitment_point")
                                     if row["dwelling"][name]["active"])
        if dwelling_components:
            row["development_while_dwelling"] = {
                "components": dwelling_components,
                "writes": [event["process"] for event in row["events"] if "before" in event
                           and "after" in event and event["before"] != event["after"]],
            }
        track(metrics, row, physical, story, signed, character_reviews)
        row["occupancy"] = occupancy(body, world, facet, external, basin, choice, seam, core.seed, len(tape), row)
        for name, value in row["occupancy"].items():
            peaks[name] = max(peaks[name], value)
    final = terrain.verify_reload()
    kernel = core.seed
    return {
        "actor": actor, "organism_id": kernel.organism_id, "birth_position": 0,
        "initial_character": initial, "enrollment": enrollment, "final_character": final,
        "kept_after_reload": True, "checkpoint": {
            "payload": kernel.checkpoint_payload(kernel.checkpoint), "signature": kernel.checkpoint_sig,
            "public_key": kernel.birth.public_key_b64,
        },
        "phase_end_commitment": seam.status(len(tape) - 1),
        "world_at_removal" if founding else "world_at_end": world.snapshot(),
        "peak_occupancy": dict(peaks), "metrics": dict(metrics), "story_readings": readings,
        "character_reviews": character_reviews, "ticks": trajectory,
    }
