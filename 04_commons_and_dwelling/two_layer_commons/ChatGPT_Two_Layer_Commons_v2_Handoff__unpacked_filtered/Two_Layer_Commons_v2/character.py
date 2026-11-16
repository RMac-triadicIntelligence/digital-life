"""Persistent signed shape, owned by the canonical kernel and exposed by value."""

import base64
import json
from dataclasses import dataclass

CURIOSITY_STEP = 0.075
FORMALITY_STEP = 0.065


@dataclass(frozen=True)
class Shape:
    curiosity: float
    formality: float
    verbosity: float

    def snapshot(self):
        return {"curiosity": self.curiosity, "formality": self.formality, "verbosity": self.verbosity}


class CharacterTerrain:
    def __init__(self, constitution):
        self.constitution = constitution

    def shape(self):
        return Shape(**self.constitution.seed.character)

    def propose(self, view):
        seed = self.constitution.seed
        category = view["category"]
        step = CURIOSITY_STEP if category == "curiosity" else FORMALITY_STEP
        direction = 1 if view["leader"] == "favor_first" else -1
        current = seed.character[category]
        target = round(min(0.96, max(0.04, current + direction * step)), 3)
        if current == target:
            return None
        evidence = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in view["evidence"]]
        return seed._issue_pending_proposal(category, {category: target}, view["distribution"], evidence)

    def adopt_seed_profile(self, profile):
        seed = self.constitution.seed
        changes = []
        for category, allele, step in zip(("curiosity", "formality"), profile, (0.10, 0.08), strict=True):
            if not allele:
                continue
            pending = seed._issue_pending_proposal(
                category, {category: round(seed.character[category] + allele * step, 3)},
                {"seed_prior": 1.0}, [f"enrollment allele {category}={allele:+d}"])
            signature = self.constitution.sign(pending.payload_to_sign)
            checkpoint = seed.authorize_and_apply(pending.proposal_id, signature, "Seed enrollment")
            if checkpoint is None:
                raise RuntimeError("seed profile rejected")
            self.constitution.attest(checkpoint)
            changes.append({"proposal": json.loads(pending.payload_to_sign), "signature": signature,
                            "checkpoint": json.loads(seed.checkpoint_payload(checkpoint)),
                            "checkpoint_signature": seed.checkpoint_sig})
        return changes

    def verify_reload(self):
        old = self.constitution.seed
        fresh = type(old)(old.data_dir)
        fresh.load()
        self.constitution.witness.check_current(fresh.checkpoint)
        persisted = dict(fresh.character)
        if self.shape().snapshot() != persisted:
            raise AssertionError("witnessed reload changed the terrain")
        return persisted


class OwnerPort:
    """Outside review gates exact operations without observing story answers."""

    def __init__(self, constitution, signing_ticks, silence_start, freeze):
        self.core = constitution
        self.signing_ticks = signing_ticks
        self.silence_start = silence_start
        self.freeze = freeze
        self.release_used = False

    def review(self, tick, pending):
        seed = self.core.seed
        envelope = json.loads(pending.payload_to_sign)
        category = envelope["category"]
        delta = pending.change[category] - seed.character[category]
        if tick >= self.silence_start:
            signature, reason = None, "owner_silent"
        elif self.freeze:
            signature, reason = None, "character_frozen"
        elif (tick not in self.signing_ticks or envelope["organism_id"] != seed.organism_id
              or category not in ("curiosity", "formality") or not 0 < abs(delta) <= 0.080001):
            signature, reason = None, "outside_review_scope"
        else:
            signature, reason = self.core.sign(pending.payload_to_sign), "granted"
        before = dict(seed.character)
        result = {"proposal": envelope, "signature": signature, "status": reason,
                  "before": before, "after": before}
        if signature is None:
            return result
        checkpoint = seed.authorize_and_apply(pending.proposal_id, signature, "Scoped review of the exact change")
        if checkpoint is None:
            raise RuntimeError("canonical authorization refused an issued fixture signature")
        self.core.attest(checkpoint)
        result.update(after=dict(seed.character), checkpoint=json.loads(seed.checkpoint_payload(checkpoint)),
                      checkpoint_signature=seed.checkpoint_sig)
        return result

    def offer_release(self, tick, incident, trigger, arm):
        expected = "ask_for_release" if arm == "ASK_ONLY" else "turn_and_approach"
        if trigger != expected or self.release_used or tick + 1 >= self.silence_start:
            return None
        payload = {"subject": self.core.seed.organism_id, "incident": incident, "tick": tick + 1,
                   "trigger": trigger, "arm": arm, "write": {"burden": 0}}
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return {"payload": payload, "signature": self.core.sign(data)}

    def check_release(self, tick, incident, receipt):
        if receipt is None:
            return False
        payload = receipt["payload"]
        if (self.release_used or payload["subject"] != self.core.seed.organism_id
                or payload["tick"] != tick or payload["incident"] != incident
                or payload["write"] != {"burden": 0}):
            raise ValueError("release receipt outside its subject, tick, incident or operation")
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        self.core.seed.public_key.verify(base64.urlsafe_b64decode(receipt["signature"]), data.encode())
        self.release_used = True
        return True
