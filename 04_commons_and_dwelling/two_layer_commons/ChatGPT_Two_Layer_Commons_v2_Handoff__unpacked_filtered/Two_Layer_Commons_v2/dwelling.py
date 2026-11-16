"""Four distinct forms of holding an unresolved state."""

from collections import deque
from dataclasses import dataclass
import math

from protocol import CATEGORIES

BASIN_CAPACITY = 5  # Per category.
BASIN_TTL = 7
FACET_NAMES = ("structural", "relational", "grounded")
READS = ("favor_first", "favor_second", "unmodeled_cause")


def bounded(value):
    return round(min(1.0, max(0.0, value)), 12)


def cosine(a, b):
    norm = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    if not norm:
        return 0.0
    return round(min(1.0, max(-1.0, sum(x * y for x, y in zip(a, b, strict=True)) / norm)), 12)


class FacetDwelling:
    def __init__(self):
        self.facets = (0.35, 0.50, 0.30)
        self.field = 0.0

    def step(self, stimuli, depth, failed):
        previous = self.facets
        if not failed:
            drift = tuple(0.25 * (value - current) for current, value in zip(previous, stimuli, strict=True))
            self.facets = tuple(bounded(value + drift[index] + 0.12 * (sum(previous) - 3 * value))
                                for index, value in enumerate(previous))
            coherence = 1 - (max(self.facets) - min(self.facets))
            rise = 0.24 * depth * (1 - coherence) * (1 - self.field)
            fade = 0.045 * coherence * self.field
            self.field = bounded(self.field + rise - fade)

    def snapshot(self):
        return {"facets": dict(zip(FACET_NAMES, self.facets, strict=True)), "field": self.field}


class WorldDwelling:
    def __init__(self):
        self.field = 0.0
        self.coherence = 0.0

    def step(self, state, external, failed):
        if failed:
            return
        self.coherence = cosine(state, external)
        uncertainty = 1 - abs(self.coherence)
        rise = 0.12 * uncertainty * (1 - self.field)
        decay = 0.08 * self.coherence * self.field
        self.field = bounded(self.field + rise - decay)

    def snapshot(self):
        return {"field": self.field, "coherence": self.coherence}


class UncertaintyBasin:
    """Bounded pre-traces, with corroboration, depth and a reserved unknown read."""

    def __init__(self, latency=False):
        self.latency = latency
        cap = 1 if latency else BASIN_CAPACITY
        self.entries = {category: deque(maxlen=cap) for category in CATEGORIES}

    def step(self, tick, social):
        expired, evicted = [], None
        for samples in self.entries.values():
            while samples and tick - samples[0][0] > BASIN_TTL:
                expired.append(samples.popleft()[1].id)
        if social is not None:
            samples = self.entries[social.category]
            if len(samples) == samples.maxlen:
                evicted = samples[0][1].id
            samples.append((tick, social))
        return {"expired": expired, "evicted": evicted}

    def snapshot(self):
        return {
            category: [social.id for _, social in samples]
            for category, samples in self.entries.items()
        }

    def category_view(self, category, tick):
        entries = self.entries[category]
        if not entries:
            return None
        log_weights = [0.0, 0.0, 0.0]
        salience = 0.0
        evidence = []
        for arrival, social in entries:
            weight = 0.72 ** (tick - arrival)
            salience += weight * (1 - max(social.distribution))
            for index, likelihood in enumerate(social.distribution):
                log_weights[index] += weight * math.log(likelihood)
            evidence.append({"encounter": social.id, "context": social.context,
                             "likelihood": list(social.distribution), "tick": arrival,
                             "weight": round(weight, 12)})
        # A timer only inspects the latest instantaneous likelihood; no aging
        # of its likelihood or accumulation over interventions.
        if self.latency:
            probabilities = list(entries[-1][1].distribution)
            salience = 1 - max(probabilities)
        else:
            offset = max(log_weights)
            normalized = [math.exp(value - offset) for value in log_weights]
            probabilities = [round(value / sum(normalized), 12) for value in normalized]
        leader = max(range(3), key=probabilities.__getitem__)
        context_count = len({social.context for _, social in entries})
        opposing_margin = abs(probabilities[0] - probabilities[1])
        return {
            "category": category,
            "distribution": dict(zip(READS, probabilities, strict=True)),
            "leader": READS[leader],
            "salience": round(salience, 12),
            "contexts": context_count,
            "evidence": evidence,
            "can_propose": leader != 2 and probabilities[leader] >= 0.59 and opposing_margin >= 0.20
                           and (self.latency or (len(entries) >= 2 and context_count >= 2)),
            "can_ask": leader == 2 or salience >= 0.42,
        }

    def views(self, tick):
        return tuple(view for category in CATEGORIES
                     if (view := self.category_view(category, tick)) is not None)

    def surface(self, category):
        # A surfaced pre-trace leaves the basin. The external trace keeps
        # provenance; the member retains no interview transcript.
        self.entries[category].clear()


class CommitmentPoint:
    """An exact proposed change can persist unresolved with capability present."""

    CAPACITY = 1

    def __init__(self):
        self.open = None

    def submit(self, pending):
        if self.open is not None:
            raise RuntimeError("existing commitment point is unresolved")
        self.open = {"proposal_id": pending.proposal_id, "payload_sha256": pending.payload_hash,
                     "since": int(pending.timestamp - 1_800_000_000)}

    def resolve(self):
        self.open = None

    def status(self, tick):
        if self.open is None:
            return {"active": False, "status": "clear"}
        return {"active": True, "status": "not_yet", "capable": True, "authorized": False,
                **self.open, "held_ticks": tick - self.open["since"] + 1}


@dataclass(frozen=True)
class DwellCue:
    facet_hold: bool
    world_hold: bool
    differentiated: bool
    situational_mismatch: bool


def dwelling_permissions(tick, facet, world, yoke):
    if yoke is None:
        facet_hold, world_hold = facet.field >= 0.13, world.field >= 0.16
        return DwellCue(facet_hold, world_hold,
                        facet_hold and max(facet.facets) - min(facet.facets) >= 0.18,
                        world_hold and 1 - abs(world.coherence) >= 0.18)
    yoked = yoke[tick]
    return DwellCue(yoked["facet"], yoked["world"], False, False)
