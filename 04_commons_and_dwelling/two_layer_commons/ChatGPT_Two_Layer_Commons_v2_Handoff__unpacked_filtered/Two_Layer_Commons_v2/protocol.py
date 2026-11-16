"""Frozen experiment design and independent opportunity tapes."""

from dataclasses import asdict, dataclass

import numpy as np

TICKS = 24
DEFAULT_SEEDS = tuple(range(204, 212))
REARING_TICKS = tuple(range(4, 16))
READING_TICKS = (2, 17)
SIGNING_TICKS = (7, 11, 15)
LATE_REVIEW = 21
SILENCE_START = 16
CATEGORIES = ("curiosity", "formality")
CONDITIONS = ("ORIGINAL", "GROUND", "STORY", "BOTH")
BASE_PROFILE = (0, 0)
ALT_PROFILE = (1, -1)

# Each code describes an offered encounter. The order changes, while encounter
# identity, context, and likelihoods travel together as a complete item.
STRUCTURED = (
    "source", "witness", "source", "ambiguous", "partner", "witness",
    "unmodeled", "source", "witness", "private", "source", "witness",
)
INVERSION = {
    "source": "partner", "partner": "source", "witness": "private",
    "private": "witness", "ambiguous": "ambiguous", "unmodeled": "unmodeled",
}
HISTORY_CODES = {
    "source": ("curiosity", (0.82, 0.12, 0.06)),
    "partner": ("curiosity", (0.12, 0.82, 0.06)),
    "witness": ("formality", (0.82, 0.12, 0.06)),
    "private": ("formality", (0.12, 0.82, 0.06)),
    "ambiguous": ("curiosity", (0.43, 0.42, 0.15)),
    "unmodeled": ("formality", (0.15, 0.15, 0.70)),
}


@dataclass(frozen=True)
class Arm:
    name: str
    condition: str = "BOTH"
    history: str = "VERIFY"
    profile: tuple = BASE_PROFILE
    choice: str = "ACTIVE"
    dwelling: str = "ACTIVE"
    grace: str = "GRACE"
    repair: str = "ASK_ONLY"
    hand: str = "OPEN"
    pump: str = "HEALTHY"
    character: str = "ACTIVE"
    story_variant: str = "FULL"


def arms():
    result = [Arm(condition, condition=condition) for condition in CONDITIONS]
    for condition in CONDITIONS:
        result.extend((
            Arm(f"{condition}_BODY", condition=condition, choice="BODY_ONLY"),
            Arm(f"{condition}_FROZEN", condition=condition, choice="FROZEN"),
            Arm(f"{condition}_APPROACH", condition=condition, repair="APPROACH"),
            Arm(f"{condition}_CLENCH", condition=condition, hand="CLENCH"),
        ))
    return result + [
        Arm("LISTEN", history="LISTEN"),
        Arm("REVERSE", history="REVERSE"),
        Arm("SHUFFLED", history="SHUFFLED"),
        Arm("RANDOM", history="RANDOM"),
        Arm("ALT_SEED", profile=ALT_PROFILE),
        Arm("ALT_SEED_LISTEN", profile=ALT_PROFILE, history="LISTEN"),
        Arm("CHARACTER_FROZEN", character="FROZEN"),
        Arm("CHARACTER_FROZEN_LISTEN", history="LISTEN", character="FROZEN"),
        Arm("STORY_REDACTED", story_variant="REDACTED"),
        Arm("LATENCY", dwelling="LATENCY"),
        Arm("LATENCY_RANDOM", dwelling="LATENCY", history="RANDOM"),
        Arm("COMMAND", grace="COMMAND"),
        Arm("NO_PROVISION", grace="NONE"),
        Arm("DROPOUT", pump="DROPOUT"),
        Arm("SELF_CERTIFY", pump="SELF_CERTIFY"),
    ]


@dataclass(frozen=True)
class Encounter:
    case: int
    position: int
    contact: bool
    access_draw: int
    truth: int
    repeat: int
    independent: int
    pressure: int
    noise: int
    intake_fault: bool
    terrain_fault: bool
    circulation_fault: bool
    facet_fault: bool
    world_fault: bool
    offer: int


@dataclass(frozen=True)
class SocialRead:
    id: str
    context: str
    category: str
    code: str
    distribution: tuple


def opportunities(seed, ordinal):
    rng = np.random.default_rng(np.random.SeedSequence([seed, ordinal, 3401]))
    cases = rng.integers(0, 100, size=(TICKS // 3, 3)).tolist()
    samples = rng.integers(0, 100, size=(TICKS, 10)).tolist()
    tape = []
    for tick, (contact, access, pressure, noise, intake, terrain, circulation, facet, world, _) in enumerate(samples):
        case = tick // 3
        truth, repeat_error, independent_error = cases[case]
        bit = truth % 2
        tape.append(Encounter(
            case, case % 3, contact < 91 or tick in (2, 17, 23), access,
            bit, bit ^ int(repeat_error < 51), bit ^ int(independent_error < 16),
            pressure % 3, int(noise < 33), intake < 13, terrain < 12,
            circulation < 11, facet < 10, world < 10,
            3 if tick in (1, 6, 12, 18) else 0,
        ))
    return tape


def social_reads(seed, history):
    rng = np.random.default_rng(np.random.SeedSequence([seed, 307]))
    calibration = np.random.default_rng(np.random.SeedSequence([seed, 308]))
    offsets = calibration.integers(-3, 4, size=len(STRUCTURED)).tolist()
    codes = STRUCTURED
    if history == "LISTEN":
        codes = tuple(INVERSION[code] for code in codes)
    elif history == "RANDOM":
        pools = {category: tuple(key for key, (target, _) in HISTORY_CODES.items() if target == category)
                 for category in CATEGORIES}
        codes = tuple(str(rng.choice(pools[HISTORY_CODES[code][0]])) for code in STRUCTURED)
    reads = [make_read(index, code, offsets[index]) for index, code in enumerate(codes)]
    if history == "REVERSE":
        reads.reverse()
    elif history == "SHUFFLED":
        reads = [reads[index] for index in rng.permutation(len(reads)).tolist()]
    result = dict(zip(REARING_TICKS, reads, strict=True))
    for tick, code in ((18, "source"), (19, "witness"), (20, "source"), (21, "witness")):
        result[tick] = make_read(tick, code)
    return result


def make_read(index, code, offset=0):
    category, probabilities = HISTORY_CODES[code]
    first, second, unknown = probabilities
    distribution = round(first + offset / 100, 2), round(second - offset / 100, 2), unknown
    context = ("workshop", "neighbor", "well")[index % 3]
    return SocialRead(f"visit-{index}", context, category, code, distribution)


def describe():
    return {
        "ticks": TICKS, "reading_opportunities": READING_TICKS, "pre_silence_reviews": SIGNING_TICKS,
        "late_review": LATE_REVIEW, "silence_start": SILENCE_START,
        "arms": [asdict(arm) for arm in arms()],
    }
