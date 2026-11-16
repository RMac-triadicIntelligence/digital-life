"""Automatic physiology; the scheduler supplies physical inputs every tick."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Sensation:
    short: bool
    settled: bool
    independent_available: bool
    needs_repair: bool


@dataclass(frozen=True)
class PhysicalInputs:
    contact: bool
    friction: int
    abrasion: int
    pulse: int
    noise: int
    intake_fault: bool
    regulation_fault: bool
    circulation_fault: bool
    clench: bool
    release: bool


class Body:
    ENERGY_CAPACITY = 8
    HAND_CAPACITY = 2
    EVIDENCE_CAPACITY = 8
    TERRAIN_CAPACITY = 6

    def __init__(self):
        self.reserve = 4
        self.terrain = {"adaptation": 0, "burden": 0}
        self.evidence = 0
        self.hand = 0
        self.settled = False

    def step(self, inputs):
        old = self.snapshot()
        self.reserve = max(0, self.reserve - (3 if inputs.regulation_fault else 2))
        if inputs.contact and not inputs.intake_fault:
            self.reserve = min(self.ENERGY_CAPACITY, self.reserve + 3 - inputs.friction)
        if inputs.contact and not inputs.regulation_fault:
            self.evidence = min(self.EVIDENCE_CAPACITY, self.evidence + 2 - inputs.friction)
            self.terrain["adaptation"] = min(self.TERRAIN_CAPACITY,
                                             self.terrain["adaptation"] + 1 + inputs.noise)
        self.terrain["burden"] = min(self.TERRAIN_CAPACITY,
                                     self.terrain["burden"] + inputs.abrasion)
        if inputs.release:
            self.terrain["burden"] = 0
        before_boundary = 5 + old["terrain"]["burden"] - old["terrain"]["adaptation"] // 2
        boundary = 5 + self.terrain["burden"] - self.terrain["adaptation"] // 2
        self.settled = self.evidence >= boundary
        # Grace has its own provision channel and never enters the terrain update.
        offered = inputs.pulse
        received = 0 if inputs.circulation_fault else min(offered, self.HAND_CAPACITY - self.hand)
        self.hand += received
        forwarded = 0
        if not inputs.circulation_fault and not inputs.clench:
            forwarded = offered - received + max(0, self.hand - 1)
            self.hand = min(self.hand, 1)
        blocked = offered - received if inputs.circulation_fault or inputs.clench else 0
        return {
            "before": old, "after": self.snapshot(),
            "boundary_before": before_boundary, "boundary_after": boundary,
            "grace": {"offered": offered, "received": received,
                      "forwarded": forwarded, "blocked": blocked,
                      "unready_before": not old["settled"]},
            "faults": {"intake": inputs.intake_fault, "regulation": inputs.regulation_fault,
                       "circulation": inputs.circulation_fault},
        }

    def snapshot(self):
        return {"reserve": self.reserve, "terrain": dict(self.terrain),
                "evidence": self.evidence, "hand": self.hand, "settled": self.settled}
