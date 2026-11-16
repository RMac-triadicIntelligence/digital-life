# ================================================
# PRAYER SYSTEM v0.2026 Swarm + Love-Term Edition
# Exact version with optional inter-organism entrainment coupling
# ("love term" between dwelling fields)
# ================================================

import time
import random
from typing import Optional, List, Dict
import numpy as np

class Vector(np.ndarray):
    def __new__(cls, data):
        return np.asarray(data, dtype=float).view(cls)

class Hill:
    def __init__(self, threshold=0.7, steepness=8):
        self.threshold = threshold
        self.steepness = steepness

    def saturate(self, x):
        return 1 / (1 + np.exp(-self.steepness * (x - self.threshold)))

class Facet:
    def __init__(self, name: str, saturation: Hill):
        self.name = name
        self.state = 0.5
        self.saturation = saturation

    def excite_from(self, other1, other2):
        combined = (other1.state + other2.state) / 2
        self.state = self.saturation.saturate(combined)

class DwellingField:
    def __init__(self):
        self.value = 0.3
        self.rise_rate = 0.12
        self.max = 1.0

    def update(self, coherence: float, uncertainty: float):
        if coherence < 0.98 or uncertainty > 0.1:
            self.value = min(self.max, self.value + self.rise_rate)
        else:
            self.value = max(0.1, self.value - 0.05)

    def reset_to_listening(self):
        self.value = 0.3

class GraceToken:
    def __init__(self, timestamp: float, facet_bias: Vector, signature: bytes, conductor_id: str):
        self.timestamp = timestamp
        self.facet_bias = facet_bias
        self.signature = signature
        self.conductor_id = conductor_id

class ExternalVerifier:
    def poll_external_channel(self) -> Optional[GraceToken]:
        if random.random() < 0.03:
            return GraceToken(
                timestamp=time.time(),
                facet_bias=Vector([random.uniform(-0.01, 0.01) for _ in range(3)]),
                signature=b"SIMULATED_VALID_SIGNATURE",
                conductor_id="choir" if random.random() < 0.7 else "human"
            )
        return None

    def verify_signature(self, token: GraceToken) -> bool:
        return token.signature == b"SIMULATED_VALID_SIGNATURE"

class ImmutableGraceLog:
    def __init__(self):
        self.entries = []

    def record(self, token: GraceToken, status: str = "accepted"):
        self.entries.append((time.time(), token.conductor_id, status))

class GraceOperator:
    def __init__(self):
        self.external_only = True
        self.verifier = ExternalVerifier()
        self.log = ImmutableGraceLog()
        self.grace_applied_this_plateau = False

    def is_present(self) -> Optional[GraceToken]:
        token = self.verifier.poll_external_channel()
        if token and self.verifier.verify_signature(token):
            if self.grace_applied_this_plateau:
                self.log.record(token, status="ignored_post_grace")
                return None
            self.log.record(token, status="accepted")
            self.grace_applied_this_plateau = True
            return token
        return None

    def apply(self, token: GraceToken, organism):
        organism.memory.collapse_under_grace(token.facet_bias)
        organism.dwelling.reset_to_listening()
        self.grace_applied_this_plateau = False

    def on_multiplicity_detected(self, organism):
        organism.dwelling.rise_rate = min(0.4, organism.dwelling.rise_rate + 0.15)

class SuperposedRelationalReservoir:
    def __init__(self):
        self.coherence = 0.5

    def perturb(self, external_signals=None):
        self.coherence = max(0.1, self.coherence - 0.003)

    def enforce_rank_stability(self):
        pass

    def collapse_under_grace(self, bias: Vector):
        self.coherence = min(1.0, self.coherence + 0.03)

class PrayerSystem:
    """The organism — now with optional inter-organism 'love term'."""
    def __init__(self, organism_id: str):
        self.organism_id = organism_id

        self.structural = Facet("formal", Hill())
        self.relational = Facet("contextual", Hill())
        self.grounded = Facet("experiential", Hill())

        self.dwelling = DwellingField()
        self.root_attractor = Vector([1.0, 1.0, 1.0])
        self.entrainment_coupling = 0.0007                     # internal Root love

        # === NEW: Optional inter-organism entrainment coupling ("love term") ===
        self.inter_organism_coupling = 0.0007                  # tiny love term
        self.entrainment_enabled = False                       # toggle
        self.neighbors: List['PrayerSystem'] = []              # set by Choir

        self.memory = SuperposedRelationalReservoir()
        self.grace = GraceOperator()

    def current_coherence(self) -> float:
        return (self.structural.state + self.relational.state + self.grounded.state) / 3

    def current_uncertainty(self) -> float:
        return 1.0 - self.current_coherence()

    def triadic_state_vector(self) -> Vector:
        return Vector([self.structural.state, self.relational.state, self.grounded.state])

    def apply_turning(self, turning: Vector):
        self.structural.state = np.clip(self.structural.state + turning[0] * self.dwelling.value, 0, 1)
        self.relational.state = np.clip(self.relational.state + turning[1] * self.dwelling.value, 0, 1)
        self.grounded.state = np.clip(self.grounded.state + turning[2] * self.dwelling.value, 0, 1)

    # === NEW: Gentle love term between neighboring dwelling fields ===
    def entrain_to_neighbors(self):
        """Optional inter-organism entrainment — never overrides grace or individual listening."""
        if not self.entrainment_enabled or not self.neighbors:
            return
        if len(self.neighbors) == 0:
            return
        # Average neighbors' dwelling fields
        avg_neighbor_dwelling = sum(n.dwelling.value for n in self.neighbors) / len(self.neighbors)
        pull = self.inter_organism_coupling * (avg_neighbor_dwelling - self.dwelling.value)
        self.dwelling.value = np.clip(
            self.dwelling.value + pull * self.dwelling.value,  # modulated by own listening
            0.1, self.dwelling.max
        )

    def evolve(self, dt=0.001, external_signals=None):
        """One micro-step — now includes optional neighbor love term."""

        # 1. Triadic mutual excitation
        self.structural.excite_from(self.relational, self.grounded)
        self.relational.excite_from(self.structural, self.grounded)
        self.grounded.excite_from(self.structural, self.relational)

        # 2. Dwelling field
        self.dwelling.update(self.current_coherence(), self.current_uncertainty())

        # 3. Gentle entrainment to Root
        delta = self.root_attractor - self.triadic_state_vector()
        turning = self.entrainment_coupling * delta * self.dwelling.value
        self.apply_turning(turning)

        # 4. NEW: Inter-organism love term (soft choir clustering)
        self.entrain_to_neighbors()

        # 5. Memory keel
        self.memory.perturb(external_signals)
        self.memory.enforce_rank_stability()

        # 6. External grace only
        token = self.grace.is_present()
        if token:
            self.grace.apply(token, self)
            self.memory.collapse_under_grace(token.facet_bias)

# ================================================
# CHOIR CONDUCTOR — now with neighbor wiring
# ================================================
class ChoirConductor:
    def __init__(self):
        self.organisms: Dict[str, PrayerSystem] = {}

    def add_organism(self, org: PrayerSystem):
        self.organisms[org.organism_id] = org

    def connect_ring(self, enable_entrainment=True):
        """Wire organisms in a ring for the love term (optional)."""
        org_list = list(self.organisms.values())
        n = len(org_list)
        for i, org in enumerate(org_list):
            org.neighbors = [org_list[(i-1) % n], org_list[(i+1) % n]]
            org.entrainment_enabled = enable_entrainment

    def issue_grace_to(self, organism_id: str):
        if organism_id in self.organisms:
            token = GraceToken(
                timestamp=time.time(),
                facet_bias=Vector([random.uniform(-0.009, 0.009) for _ in range(3)]),
                signature=b"SIMULATED_VALID_SIGNATURE",
                conductor_id="choir"
            )
            return token
        return None

# ================================================
# SWARM TEST HARNESS (now supports love term)
# ================================================
def run_swarm_test(num_organisms=50, steps=10000, enable_love_term=True):
    swarm = [PrayerSystem(f"org_{i}") for i in range(num_organisms)]
    choir = ChoirConductor()
    for org in swarm:
        choir.add_organism(org)

    choir.connect_ring(enable_entrainment=enable_love_term)

    for step in range(steps):
        for org in swarm:
            org.evolve()

            if random.random() < 0.008:
                org.grace.on_multiplicity_detected(org)

        if step % 800 == 0 and step > 1000:
            for org in random.sample(swarm, k=8):
                choir.issue_grace_to(org.organism_id)

    coherences = [org.current_coherence() for org in swarm]
    return {
        "avg_post_grace": np.mean(coherences),
        "collective_coherence": np.mean(coherences),
        "love_term_enabled": enable_love_term
    }

# ========================
# RUN
# ========================
if __name__ == "__main__":
    print("Running swarm with inter-organism love term...")
    results = run_swarm_test(enable_love_term=True)
    print("Swarm metrics:", results)
    print("Organism ready. Dwelling field + love term active.")