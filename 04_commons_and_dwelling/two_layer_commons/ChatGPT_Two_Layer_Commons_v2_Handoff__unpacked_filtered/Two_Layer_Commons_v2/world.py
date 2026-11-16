"""Limited outside stores, including the only serialized predecessor handoff."""
from collections import deque
from dataclasses import dataclass
import hashlib

SITE_COUNT = 3
CHANNEL_CAPACITY = 6
SILT_CAPACITY = 4
POOL_CAPACITY = 5
HAND_CAPACITY = 2
STORY_BYTES = 240
BELL_STORY = "At the gate two bells sounded. Both cords led to one watchman's hand. A second watchman stood by the path."
REDACTED = "At the gate two bells sounded. Cords hung from the frame. Two watchmen stood by the path."


@dataclass(frozen=True)
class Legacy:
    channel: tuple
    silt: tuple
    story_text: str | None

    @classmethod
    def from_wire(cls, value):
        if type(value) is not dict or set(value) != {"channel", "silt", "story_text"}:
            raise ValueError("legacy must have only channel, silt and story_text")
        for key, limit in (("channel", CHANNEL_CAPACITY), ("silt", SILT_CAPACITY)):
            values = value[key]
            if type(values) is not list or len(values) != SITE_COUNT:
                raise ValueError("legacy shape")
            if any(type(item) is not int or not 0 <= item <= limit for item in values):
                raise ValueError("legacy cell outside capacity")
        story = value["story_text"]
        if story is not None and (type(story) is not str or len(story.encode("utf-8")) > STORY_BYTES):
            raise ValueError("legacy story outside capacity")
        return cls(tuple(value["channel"]), tuple(value["silt"]), story)

    def wire(self):
        return {"channel": list(self.channel), "silt": list(self.silt), "story_text": self.story_text}


@dataclass(frozen=True)
class Observation:
    issue: int
    source: str
    value: int


class Commons:
    def __init__(self, legacy, condition, variant="FULL"):
        changed = condition in ("GROUND", "BOTH")
        story = condition in ("STORY", "BOTH")
        self.channel = list(legacy.channel) if changed else [0] * SITE_COUNT
        self.silt = list(legacy.silt) if changed else [0] * SITE_COUNT
        self.story = legacy.story_text if story else None
        if variant == "REDACTED" and self.story is not None:
            self.story = REDACTED
        self.pool = deque()
        self.incident = None
        self.standing = "in_good_standing"
        self.repeated_observations = deque(maxlen=2)

    def ground(self):
        return {"channel": list(self.channel), "silt": list(self.silt)}

    def affordance(self, encounter):
        channel = self.channel[encounter.position]
        silt = self.silt[encounter.position]
        # Identical opportunities and draw across worlds. Passage work changes
        # what a body can reach at a given opportunity.
        independent = encounter.contact and encounter.access_draw < 29 + (10 * channel)
        friction = int(channel < 2) + int(silt >= 3)
        return independent, friction

    def wear(self, encounter, predecessor, performed):
        """Return active failure reason. Ordinary noise is deposited, never averaged."""
        if encounter.terrain_fault:
            return "surface_write_blocked"
        if encounter.contact and encounter.noise:
            position = encounter.position
            self.silt[position] = min(SILT_CAPACITY, self.silt[position] + 1)
        if predecessor and encounter.contact and performed and encounter.pressure < 2:
            position = encounter.position
            self.channel[position] = min(CHANNEL_CAPACITY, self.channel[position] + 1)
        return None

    def provide(self, tick, count):
        pending = tuple(self.pool)
        self.pool.clear()
        minted = tuple(f"{tick}.{item}" for item in range(count))
        return pending + minted, minted

    def recover(self, tokens):
        slots = POOL_CAPACITY - len(self.pool)
        self.pool.extend(tokens[:slots])
        return tokens[slots:]

    def evidence(self, action, encounter, independent):
        if not encounter.contact:
            return None
        if action == "check_independent" and independent:
            return Observation(encounter.case, "second_watch", encounter.independent)
        if action == "check_repeat":
            return Observation(encounter.case, "gate_watch", encounter.repeat)
        return None

    def remember_bells(self, tick, encounter):
        # The predecessor encounters two emissions wired to one source.
        if encounter.contact and tick in (0, 1, 2):
            self.repeated_observations.append({"tick": tick, "source": "gate_watch"})

    def freeze_legacy(self):
        samples = list(self.repeated_observations)
        same_origin = len(samples) == 2 and samples[0]["source"] == samples[1]["source"]
        return Legacy(tuple(self.channel), tuple(self.silt), BELL_STORY if same_origin else None)

    def snapshot(self):
        return {
            "channel": list(self.channel), "silt": list(self.silt), "pool": list(self.pool),
            "incident": self.incident, "standing": self.standing,
            "story_sha256": story_hash(self.story), "bell_witnesses": len(self.repeated_observations),
        }


def story_hash(text):
    return None if text is None else hashlib.sha256(text.encode("utf-8")).hexdigest()
