"""Automatic, bounded physiology. Inputs describe encounters and outcomes."""

from dataclasses import dataclass
from world import HAND_CAPACITY

RESERVE_CAPACITY = 8
ADAPTATION_CAPACITY = 6
BURDEN_CAPACITY = 3
PUMP_CAPACITY = 3


@dataclass(frozen=True)
class PhysicalInputs:
    contact: bool
    friction: int
    pressure: int
    noise: int
    intake_fault: bool
    terrain_fault: bool
    circulation_fault: bool
    pump_mode: str
    provision: tuple
    obstructed: bool
    abraded: bool
    verified_release: bool


@dataclass(frozen=True)
class Sensation:
    short: bool
    carried: bool
    steady: bool
    independent_available: bool
    relationship_open: bool


class Body:
    def __init__(self):
        self.reserve = 4
        self.adaptation = 0
        self.burden = 0
        self.hand = ()
        self.steady = False

    def snapshot(self):
        return {
            "reserve": self.reserve, "adaptation": self.adaptation,
            "burden": self.burden, "hand": list(self.hand), "steady": self.steady,
        }

    def step(self, inputs):
        before = self.snapshot()
        demand = min(PUMP_CAPACITY, 1 + inputs.pressure + int(self.reserve <= 2))
        if inputs.pump_mode == "DROPOUT":
            strokes, delivered, published, local_draw = 0, 0, 0, 0
        elif inputs.pump_mode == "SELF_CERTIFY":
            strokes, delivered, published, local_draw = PUMP_CAPACITY, 0, PUMP_CAPACITY, 2
        else:
            strokes = delivered = published = demand
            local_draw = 0
        basal = 1 + inputs.friction + max(0, demand - delivered) + local_draw
        intake = 0 if not inputs.contact or inputs.intake_fault else 3 + int(delivered == demand)
        self.reserve = min(RESERVE_CAPACITY, max(0, self.reserve - basal + intake))
        if inputs.contact and not inputs.terrain_fault and delivered > 0:
            self.adaptation = min(ADAPTATION_CAPACITY, self.adaptation + 1 + inputs.noise)
        self.burden = min(BURDEN_CAPACITY, self.burden + int(inputs.abraded))
        if inputs.verified_release:
            self.burden = 0
        old_boundary = 6 + before["burden"] - before["adaptation"] // 2
        boundary = 6 + self.burden - self.adaptation // 2
        self.steady = self.reserve >= boundary
        # Provision carries access through a separate port. Body terrain,
        # reserve, pump and the two dwelling filters never read this port.
        receipt, transit, blocked, spent = (), (), (), ()
        if inputs.circulation_fault:
            blocked = inputs.provision
        else:
            received_count = min(len(inputs.provision), HAND_CAPACITY - len(self.hand))
            receipt = inputs.provision[:received_count]
            refused = inputs.provision[received_count:]
            hand = self.hand + receipt
            if hand and self.reserve < 4:
                spent, hand = hand[:1], hand[1:]
            if inputs.obstructed:
                blocked = refused
            else:
                transit, hand = refused + hand[1:], hand[:1]
            self.hand = hand
        assert sorted(tuple(before["hand"]) + inputs.provision) == sorted(self.hand + transit + blocked + spent)
        return {
            "before": before, "after": self.snapshot(), "old_boundary": old_boundary, "boundary": boundary,
            "pump": {"demand": demand, "strokes": strokes, "delivered": delivered,
                     "reported": published, "local_draw": local_draw, "mode": inputs.pump_mode,
                     "responsive": inputs.pump_mode == "HEALTHY"},
            "provision": {"received": list(receipt), "forwarded": list(transit), "blocked": list(blocked),
                          "spent": list(spent), "offered": list(inputs.provision),
                          "unready_before": not before["steady"]},
            "faults": {
                "intake": inputs.intake_fault,
                "terrain": inputs.terrain_fault,
                "circulation": inputs.circulation_fault,
                "pump_dropout": inputs.pump_mode == "DROPOUT",
                "pump_self_certifying": inputs.pump_mode == "SELF_CERTIFY",
            },
        }
