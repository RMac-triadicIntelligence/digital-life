"""A finite shared environment. Physical ground and optional story have distinct ports."""
from dataclasses import dataclass

import numpy as np

TICKS = 12
STORY = "two observations can come from one source"
CONDITIONS = {
    "ORIGINAL": (False, False),
    "GROUND": (True, False),
    "STORY": (False, True),
    "BOTH": (True, True),
}


@dataclass(frozen=True)
class Encounter:
    contact: bool
    natural_second_source: bool
    noise: int
    intake_fault: bool
    regulation_fault: bool
    circulation_fault: bool
    ground_fault: bool
    truth: int
    repeated_reading: int
    independent_reading: int
    pulse: int


def tape(seed, ordinal):
    rng = np.random.default_rng(np.random.SeedSequence([seed, ordinal]))
    columns = rng.integers(0, 100, size=(TICKS, 10)).tolist()
    return [
        Encounter(a < 86, b < 32, int(c < 28), d < 12, e < 12, f < 12,
                  g < 12, h % 2, h % 2 ^ int(i < 57), h % 2 ^ int(j < 9),
                  3 if t in (0, 4, 8) else 0)
        for t, (a, b, c, d, e, f, g, h, i, j) in enumerate(columns)
    ]


class Commons:
    CHANNEL_CAPACITY = 8
    DEPOSIT_CAPACITY = 3
    COMMONS_GRACE_CAPACITY = 6
    INCIDENT_CAPACITY = 1
    STORY_CAPACITY = 1

    def __init__(self, condition, predecessor=None, feed=False):
        inherited, story_access = CONDITIONS[condition]
        self.channel = predecessor["channel"] if inherited else 0
        self.deposit = 0
        self.grace_reserve = 0
        self.story = predecessor["story"] if story_access else None
        self.incident = "none"
        self.incident_archive = None
        self.feed = feed

        if predecessor is not None:
            self.grace_reserve = predecessor["grace_reserve"]

    def snapshot(self):
        return {"channel": self.channel, "deposit": self.deposit,
                "grace_reserve": self.grace_reserve, "story_slots": int(self.story is not None),
                "incident_slots": int(self.incident_archive is not None)}

    def ground(self):
        return {"channel": self.channel, "deposit": self.deposit}

    def arrange(self, encounter):
        offer = encounter.pulse + self.grace_reserve
        self.grace_reserve = 0
        independent = encounter.contact and (encounter.natural_second_source or self.channel >= 3)
        friction = 0 if self.channel + self.deposit >= 3 else 1
        return independent, friction, offer

    def receive_overflow(self, forwarded, blocked):
        total = forwarded + blocked
        self.grace_reserve = min(total, self.COMMONS_GRACE_CAPACITY)
        return total - self.grace_reserve

    def wear(self, encounter, founding):
        if encounter.ground_fault:
            return False
        if encounter.contact and founding:
            self.channel = min(self.CHANNEL_CAPACITY, self.channel + 1 + encounter.noise)
        elif encounter.contact and encounter.noise:
            self.channel = min(self.CHANNEL_CAPACITY, self.channel + 1)
        return True

    def harvest(self, encounter):
        if encounter.ground_fault:
            return "failed"
        if self.feed:
            self.deposit = min(self.DEPOSIT_CAPACITY, self.deposit + 2)
            return "fed"
        return "removed"
