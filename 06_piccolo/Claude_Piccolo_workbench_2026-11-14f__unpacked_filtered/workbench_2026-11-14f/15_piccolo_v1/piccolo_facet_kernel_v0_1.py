#!/usr/bin/env python3
"""
Piccolo facet kernel v0.1 — the owner signs a facet, never a number
====================================================================

A NEW LINE BESIDE Humble Seed v0.7.1, made from its source by make_facet_kernel.py (diff: FACET_KERNEL.diff).
v0.7.1 (sha256 8b849cd0710c8c33a0657f09b65da71ff7bf933d9ed3e947ec27f91e297d367b) is not edited and remains the
control. This line has a different constitution, so a different birth: no v0.7.1 state loads here and no state
from here loads on v0.7.1.

What changes
  * Character is a crystal: for each of the three faces (verbosity, formality, curiosity) an ordered list of
    facets. A facet is {place: [x, y], day: n, grown_from: sha256 of the deposit it grew from}.
  * The only write to the crystal is one append, through the owner's signature. No proposal shape removes or
    alters a facet. There is no value range and no cap.
  * The keyword interpreter and its one sanctioned move (down by 0.25) are removed. propose_facet() raises a
    proposal; dwell() lays a non-authorizing trace entry.
  * verify() also checks that the crystal holds exactly as many facets as there have been signed mutations.

What does not change
  Everything else in v0.7.1: the owner's key is outside the organism; the signature is bound to the exact
  change, its evidence and the state it was read from (F2, F4); stale, expired, replayed, forged and
  cross-category proposals are refused (F3); the first-commit flag is derived from state (G1); every result
  is owner-attested and an applied-but-unattested state does not load (O1); the witness and the audit path
  are v0.7.1's, including I1 and I2. Known open on v0.7 and v0.7.1, and NOT closed here: rollback when the
  witness is lost, and a forged ordinary event in the unattested tail.

Standing: the keel ruled "not a counter" and "no down". What the owner signs on this line is the
conductor's recommendation, not yet ruled. The constitution wording below is the conductor's draft.

Known cost, left as is: each mutation record keeps a snapshot of the whole prior crystal, as v0.7.1 kept the
prior numbers. Fine at test scale; it grows with the square of the facet count.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


SCHEMA_VERSION = "piccolo-facet-0.1"

ALLOWED_CHARACTER_FIELDS = {"verbosity", "formality", "curiosity"}
FACET_FIELDS = ("day", "grown_from", "place")
PLACE_MAX = 65535
PROPOSAL_TTL_SECONDS = 3600.0

NON_AUTHORIZING_EVENTS = {"birth", "dwelling", "authorization_rejected", "checkpoint"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _fixed(t: float) -> str:
    return f"{t:.6f}"


def _chain_head(entries: List[Dict[str, Any]]) -> str:
    return entries[-1]["entry_hash"] if entries else "0" * 64


_HEX = set("0123456789abcdef")


def _check_facet(f: Any) -> None:
    """A mutation on this line is one facet and nothing else."""
    if isinstance(f, bool) or isinstance(f, (int, float)):
        raise ValueError("a mutation must be one facet, never a number")
    if not isinstance(f, dict):
        raise ValueError(f"a mutation must be one facet (a mapping), got {type(f).__name__}")
    if set(f.keys()) != set(FACET_FIELDS):
        raise ValueError(f"facet fields {sorted(f)} must be exactly {sorted(FACET_FIELDS)}")
    d = f["day"]
    if isinstance(d, bool) or not isinstance(d, int) or d < 0:
        raise ValueError("facet day must be a whole number, zero or more")
    g = f["grown_from"]
    if not isinstance(g, str) or len(g) != 64 or any(c not in _HEX for c in g):
        raise ValueError("facet grown_from must be 64 lowercase hex characters")
    p = f["place"]
    if not isinstance(p, (list, tuple)) or len(p) != 2:
        raise ValueError("facet place must be two whole numbers")
    for c in p:
        if isinstance(c, bool) or not isinstance(c, int) or not (0 <= c <= PLACE_MAX):
            raise ValueError("facet place must be two whole numbers in range")


def _clean_facet(f: Dict[str, Any]) -> Dict[str, Any]:
    return {"day": int(f["day"]), "grown_from": str(f["grown_from"]), "place": [int(f["place"][0]), int(f["place"][1])]}


class IntegrityError(RuntimeError):
    """Persisted state failed a structural or attestation check."""


class RollbackDetected(RuntimeError):
    """External witness observed a sequence regression or fork."""


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class BirthRecord:
    organism_id: str
    public_key_b64: str
    genesis_hash: str
    created_at: float
    constitution_hash: str


@dataclass
class PreTrace:
    category: str
    distribution: Dict[str, float]
    evidence: List[str]
    salience: float
    created_at: float


@dataclass
class PendingProposal:
    proposal_id: str
    organism_id: str
    category: str
    change: Dict[str, Any]
    change_hash: str
    distribution: Dict[str, float]
    distribution_root: str
    evidence: List[str]
    evidence_root: str
    first_commit: bool
    prior_character_root: str
    prior_trace_head: str
    mutation_sequence: int
    nonce: str
    timestamp: float
    expires_at: float
    payload_to_sign: str
    payload_hash: str


@dataclass
class MutationRecord:
    proposal_id: str
    category: str
    change: Dict[str, Any]
    distribution: Dict[str, float]
    evidence: List[str]
    first_commit: bool
    mutation_sequence: int
    authorized_at: float
    signature_b64: str
    prior_character_snapshot: Dict[str, Any]
    note: str = ""


@dataclass
class Checkpoint:
    """Owner-signed attestation over a specific organism state."""
    organism_id: str
    sequence: int
    prev_checkpoint_hash: str
    birth_root: str            # G3
    constitution_root: str     # G3
    gates_root: str            # G2
    character_root: str
    consumed_root: str
    trace_head: str
    attested_trace_len: int
    mutation_sequence: int
    timestamp: float


# ---------------------------------------------------------------------------
# The organism
#
# Contains NO signing primitive. Verification only.
# ---------------------------------------------------------------------------

class HumbleSeed:

    def __init__(self, data_dir: Path | str = "./seed_data_v05"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.organism_id: Optional[str] = None
        self.public_key: Optional[Ed25519PublicKey] = None
        self.birth: Optional[BirthRecord] = None
        self.constitution: Dict[str, Any] = {}
        self.character: Dict[str, List[Dict[str, Any]]] = {}
        self.basin: List[PreTrace] = []
        self.pending: Dict[str, PendingProposal] = {}
        self.consumed: Set[str] = set()
        self.trace: List[Dict[str, Any]] = []
        self.first_commit_pending: Dict[str, bool] = {}
        self.mutation_sequence: int = 0
        self.checkpoint: Optional[Checkpoint] = None
        self.checkpoint_sig: Optional[str] = None
        self._trace_head: str = "0" * 64

    # ------------------------------------------------------------------
    # Roots
    # ------------------------------------------------------------------

    def _character_root(self) -> str:
        return _sha256(_canonical_json(self.character))

    def _consumed_root(self) -> str:
        return _sha256(_canonical_json(sorted(self.consumed)))

    def _birth_root(self) -> str:
        return _sha256(_canonical_json(asdict(self.birth) if self.birth else {}))

    def _constitution_root(self) -> str:
        return _sha256(_canonical_json(self.constitution))

    def _gates_root(self) -> str:
        return _sha256(_canonical_json(self.first_commit_pending))

    # ------------------------------------------------------------------
    # Birth
    # ------------------------------------------------------------------

    def hatch(self) -> Tuple[str, str, Checkpoint]:
        """Returns (organism_id, owner_private_pem, genesis checkpoint request).

        The organism is NOT loadable until the owner installs a signed
        checkpoint. Fail-closed from the first instant.
        """
        if self.organism_id is not None:
            raise RuntimeError("This seed has already hatched.")

        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("ascii")
        public_b64 = base64.urlsafe_b64encode(
            public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        ).decode("ascii")

        organism_id = str(uuid.uuid4())
        created_at = time.time()

        constitution = {
            "schema_version": SCHEMA_VERSION,
            "rule": "The organism can propose its own growth but cannot authorize its own growth.",
            "theorem": "External Authorization is Necessary (McMurray 2026)",
            "invariants": [
                "No character change on a misread",
                "When unreadable, ask rather than guess",
                "Private authorization material never stored by organism",
                "Signature bound to the exact mutation, its evidence, and the state it was read from",
                "Replay and reordering of authorizations forbidden",
                "A mutation is exactly one facet appended to one face; never a number, never an interpretation label, never a removal or an alteration",
                "A change may only touch the category it was proposed under",
                "The first commitment in any category is visibly flagged to the owner",
                "Character never advances without an owner-signed attestation of the result",
                "The organism cannot detect its own rollback; an external witness must",
                "The constitution and birth record are covered by the owner attestation, not by the seal alone",
                "The first-commitment flag is derived from state, never supplied by a caller",
            ],
            "allowed_character_fields": sorted(ALLOWED_CHARACTER_FIELDS),
            "character_form": "append_only_facets",
            "facet_fields": list(FACET_FIELDS),
        }
        constitution_hash = _sha256(_canonical_json(constitution))
        genesis_hash = self._derive_genesis(
            organism_id, public_b64, created_at, constitution_hash
        )

        self.organism_id = organism_id
        self.public_key = public_key
        self.constitution = constitution
        self.birth = BirthRecord(
            organism_id=organism_id,
            public_key_b64=public_b64,
            genesis_hash=genesis_hash,
            created_at=created_at,
            constitution_hash=constitution_hash,
        )
        self.character = {k: [] for k in sorted(ALLOWED_CHARACTER_FIELDS)}   # born with three empty faces
        self._append_trace({
            "event": "birth",
            "organism_id": organism_id,
            "genesis_hash": genesis_hash,
            "constitution_hash": constitution_hash,
            "timestamp": created_at,
        })

        del private_key
        self._save()
        return organism_id, private_pem, self.checkpoint_request()

    @staticmethod
    def _derive_genesis(
        organism_id: str, public_b64: str, created_at: float, constitution_hash: str
    ) -> str:
        return _sha256("|".join(
            [organism_id, public_b64, _fixed(created_at), constitution_hash]
        ))

    # ------------------------------------------------------------------
    # Trace
    # ------------------------------------------------------------------

    def _append_trace(self, entry: Dict[str, Any]) -> None:
        entry = dict(entry)
        entry["prev_hash"] = self._trace_head
        entry["entry_hash"] = _sha256(_canonical_json(entry))
        self.trace.append(entry)
        self._trace_head = entry["entry_hash"]

    def _verify_chain(self) -> None:
        if not self.trace:
            if self._trace_head != "0" * 64:
                raise IntegrityError("Empty trace but non-genesis trace_head")
            return
        prev = "0" * 64
        for i, entry in enumerate(self.trace):
            if entry.get("prev_hash") != prev:
                raise IntegrityError(f"Hash chain broken at index {i}: prev_hash mismatch")
            body = {k: v for k, v in entry.items() if k != "entry_hash"}
            if entry.get("entry_hash") != _sha256(_canonical_json(body)):
                raise IntegrityError(f"Hash chain broken at index {i}: entry_hash mismatch")
            prev = entry["entry_hash"]
        if prev != self._trace_head:
            raise IntegrityError("trace_head does not match final entry_hash")

    # ------------------------------------------------------------------
    # Checkpoints — the external authority
    # ------------------------------------------------------------------

    @staticmethod
    def checkpoint_payload(cp: Checkpoint) -> str:
        return _canonical_json({
            "schema_version": SCHEMA_VERSION,
            "kind": "checkpoint",
            **{k: (_fixed(v) if k == "timestamp" else v) for k, v in asdict(cp).items()},
        })

    def checkpoint_request(self) -> Checkpoint:
        """Describe the CURRENT state for the owner to attest."""
        prev_hash = (
            _sha256(self.checkpoint_payload(self.checkpoint))
            if self.checkpoint else "0" * 64
        )
        return Checkpoint(
            organism_id=self.organism_id or "",
            sequence=(self.checkpoint.sequence + 1) if self.checkpoint else 0,
            prev_checkpoint_hash=prev_hash,
            birth_root=self._birth_root(),
            constitution_root=self._constitution_root(),
            gates_root=self._gates_root(),
            character_root=self._character_root(),
            consumed_root=self._consumed_root(),
            trace_head=self._trace_head,
            attested_trace_len=len(self.trace),
            mutation_sequence=self.mutation_sequence,
            timestamp=time.time(),
        )

    def install_checkpoint(self, cp: Checkpoint, signature_b64: str) -> bool:
        """Accept an owner-signed attestation of the current state."""
        if self.public_key is None:
            raise RuntimeError("Organism has not hatched.")
        try:
            self.public_key.verify(
                base64.urlsafe_b64decode(signature_b64),
                self.checkpoint_payload(cp).encode("utf-8"),
            )
        except Exception:
            return False

        expected = self.checkpoint_request()
        # Everything except the owner's timestamp must match current state.
        for f in ("organism_id", "sequence", "prev_checkpoint_hash",
                  "birth_root", "constitution_root", "gates_root", "character_root",
                  "consumed_root", "trace_head", "attested_trace_len", "mutation_sequence"):
            if getattr(cp, f) != getattr(expected, f):
                return False

        self.checkpoint = cp
        self.checkpoint_sig = signature_b64
        self._append_trace({
            "event": "checkpoint",
            "sequence": cp.sequence,
            "character_root": cp.character_root,
            "timestamp": cp.timestamp,
        })
        self._save()
        return True

    def _verify_attestation(self) -> None:
        """The core of O1. State is only trusted as far as the owner signed it."""
        if self.checkpoint is None or self.checkpoint_sig is None:
            raise IntegrityError("No owner checkpoint — state is unattested")

        try:
            self.public_key.verify(
                base64.urlsafe_b64decode(self.checkpoint_sig),
                self.checkpoint_payload(self.checkpoint).encode("utf-8"),
            )
        except Exception:
            raise IntegrityError("Checkpoint signature invalid — state is not owner-attested")

        cp = self.checkpoint
        if cp.organism_id != self.organism_id:
            raise IntegrityError("Checkpoint is for a different organism")
        if cp.birth_root != self._birth_root():
            raise IntegrityError(
                "Birth record does not match the attested checkpoint — "
                "identity or genesis was rewritten"
            )
        if cp.constitution_root != self._constitution_root():
            raise IntegrityError(
                "Constitution does not match the attested checkpoint — the organism "
                "is running under a constitution the owner never attested"
            )
        if cp.gates_root != self._gates_root():
            raise IntegrityError(
                "First-commit gates do not match the attested checkpoint"
            )
        if cp.character_root != self._character_root():
            raise IntegrityError(
                "Character does not match the attested checkpoint — "
                "unattested mutation or forged character"
            )
        if cp.consumed_root != self._consumed_root():
            raise IntegrityError("Consumed ledger does not match the attested checkpoint")
        if cp.mutation_sequence != self.mutation_sequence:
            raise IntegrityError("Mutation sequence does not match the attested checkpoint")
        if cp.attested_trace_len > len(self.trace):
            raise IntegrityError("Trace is shorter than the attested checkpoint — truncation")

        attested = self.trace[:cp.attested_trace_len]
        if _chain_head(attested) != cp.trace_head:
            raise IntegrityError("Attested trace prefix does not match checkpoint trace_head")

        # Anything appended since the last attestation must be non-authorizing.
        for i, entry in enumerate(self.trace[cp.attested_trace_len:],
                                  start=cp.attested_trace_len):
            if entry.get("event") not in NON_AUTHORIZING_EVENTS:
                raise IntegrityError(
                    f"Unattested authorizing event at trace index {i}: "
                    f"{entry.get('event')} — owner checkpoint required"
                )

    # ------------------------------------------------------------------
    # Seal + persistence
    # ------------------------------------------------------------------

    def _compute_seal(self) -> str:
        """
        Integrity digest over every mutable region. NOT an authenticity
        control on its own — an attacker can recompute it. Authenticity
        comes from the owner signature over the checkpoint. This remains
        useful for cheap corruption detection and as the thing the
        checkpoint is anchored against.
        """
        return _sha256(_canonical_json({
            "schema_version": SCHEMA_VERSION,
            "birth_root": _sha256(_canonical_json(asdict(self.birth) if self.birth else {})),
            "constitution_root": _sha256(_canonical_json(self.constitution)),
            "character_root": self._character_root(),
            "basin_root": _sha256(_canonical_json([asdict(p) for p in self.basin])),
            "pending_root": _sha256(_canonical_json(
                {pid: asdict(p) for pid, p in self.pending.items()}
            )),
            "consumed_root": self._consumed_root(),
            "gates_root": _sha256(_canonical_json(self.first_commit_pending)),
            "mutation_sequence": self.mutation_sequence,
            "trace_head": self._trace_head,
        }))

    def _state_path(self) -> Path:
        return self.data_dir / "organism_state.json"

    def _save(self) -> None:
        if self.organism_id is None or self.birth is None:
            return
        state = {
            "schema_version": SCHEMA_VERSION,
            "organism_id": self.organism_id,
            "birth": asdict(self.birth),
            "constitution": self.constitution,
            "character": self.character,
            "basin": [asdict(p) for p in self.basin],
            "pending": {pid: asdict(p) for pid, p in self.pending.items()},
            "consumed": sorted(self.consumed),
            "trace": self.trace,
            "first_commit_pending": self.first_commit_pending,
            "mutation_sequence": self.mutation_sequence,
            "trace_head": self._trace_head,
            "checkpoint": asdict(self.checkpoint) if self.checkpoint else None,
            "checkpoint_sig": self.checkpoint_sig,
            "state_seal": self._compute_seal(),
        }
        tmp = self._state_path().with_suffix(".json.tmp")
        tmp.write_text(_canonical_json(state), encoding="utf-8")
        os.chmod(tmp, 0o600)
        os.replace(tmp, self._state_path())

    def load(self) -> None:
        path = self._state_path()
        if not path.exists():
            raise FileNotFoundError("No saved organism state found.")
        data = json.loads(path.read_text(encoding="utf-8"))

        if data.get("schema_version") != SCHEMA_VERSION:
            raise IntegrityError(
                f"Schema version mismatch: file={data.get('schema_version')} "
                f"expected={SCHEMA_VERSION}"
            )

        self.organism_id = data["organism_id"]
        self.birth = BirthRecord(**data["birth"])
        self.public_key = Ed25519PublicKey.from_public_bytes(
            base64.urlsafe_b64decode(self.birth.public_key_b64)
        )
        self.constitution = data.get("constitution", {})
        self.character = data["character"]
        self.basin = [PreTrace(**p) for p in data["basin"]]
        self.pending = {pid: PendingProposal(**p) for pid, p in data.get("pending", {}).items()}
        self.consumed = set(data.get("consumed", []))
        self.trace = data["trace"]
        self.first_commit_pending = data.get("first_commit_pending", {})
        self.mutation_sequence = data.get("mutation_sequence", 0)
        self._trace_head = data.get("trace_head", "0" * 64)
        cp = data.get("checkpoint")
        self.checkpoint = Checkpoint(**cp) if cp else None
        self.checkpoint_sig = data.get("checkpoint_sig")

        self.verify(expected_seal=data.get("state_seal"))

    def verify(self, expected_seal: Optional[str] = None) -> bool:
        if self.birth is None:
            raise IntegrityError("No birth record")

        if not self.constitution:
            raise IntegrityError("Constitution missing from state — cannot verify birth binding")
        if _sha256(_canonical_json(self.constitution)) != self.birth.constitution_hash:
            raise IntegrityError(
                "Constitution does not match birth commitment — organism is not "
                "running under the constitution it was born with"
            )
        if self._derive_genesis(
            self.birth.organism_id, self.birth.public_key_b64,
            self.birth.created_at, self.birth.constitution_hash,
        ) != self.birth.genesis_hash:
            raise IntegrityError("Genesis hash does not re-derive from birth record")
        if self.birth.organism_id != self.organism_id:
            raise IntegrityError("organism_id does not match birth record")

        if set(self.character.keys()) != ALLOWED_CHARACTER_FIELDS:
            raise IntegrityError(f"Crystal faces {sorted(self.character)} are not exactly the allowed faces")
        for k, v in self.character.items():
            if not isinstance(v, list):
                raise IntegrityError(f"Face {k} is not a list of facets: {type(v).__name__}")
            for f in v:
                try:
                    _check_facet(f)
                except ValueError as e:
                    raise IntegrityError(f"Face {k} holds a malformed facet: {e}")
        if sum(len(v) for v in self.character.values()) != self.mutation_sequence:
            raise IntegrityError("Crystal does not hold exactly one facet per signed mutation")

        self._verify_chain()

        # G3 + M3: the birth entry in the trace must describe THIS birth
        # record, AND it must be the only one.
        #
        # M3 (merged from Kernel P): checking `trace[0]` alone leaves a second
        # birth event later in the chain unexamined. The chain hash covers it,
        # so it is not forgeable after the fact -- but an organism that emits
        # one is not rejected, and any consumer that scans for "the birth
        # event" rather than "trace[0]" can be pointed at the wrong one.
        # Uniqueness is cheap; ambiguity about which record is the birth
        # record is not.
        if self.trace:
            births = [i for i, e in enumerate(self.trace) if e.get("event") == "birth"]
            if births != [0]:
                raise IntegrityError(
                    f"Trace must contain exactly one birth event at index zero; "
                    f"found birth events at {births}"
                )
            b = self.trace[0]
            if b.get("organism_id") != self.organism_id:
                raise IntegrityError("Birth trace entry names a different organism")
            if b.get("genesis_hash") != self.birth.genesis_hash:
                raise IntegrityError("Birth trace entry does not match the birth record genesis")
            if b.get("constitution_hash") != self.birth.constitution_hash:
                raise IntegrityError(
                    "Birth trace entry does not match the active constitution hash"
                )

        if expected_seal is not None and expected_seal != self._compute_seal():
            raise IntegrityError("State seal mismatch — corruption or rewrite of a sealed region")

        self._verify_attestation()
        return True

    # ------------------------------------------------------------------
    # Dwelling + facet proposal (no interpreter on this line)
    # ------------------------------------------------------------------

    def dwell(self, category: str, reason: str) -> dict:
        """Lay a non-authorizing entry in the trace. Changes no character."""
        if category not in ALLOWED_CHARACTER_FIELDS:
            raise ValueError(f"Unknown face: {category}")
        self._append_trace({
            "event": "dwelling",
            "category": category,
            "reason": reason,
            "timestamp": time.time(),
        })
        self._save()
        return {"status": "dwelling"}

    def propose_facet(self, face: str, place, day: int, grown_from: str,
                      evidence: List[str], ttl: float = PROPOSAL_TTL_SECONDS) -> dict:
        """The organism proposes one facet. Nothing changes until the owner signs."""
        facet = {"place": place, "day": day, "grown_from": grown_from}
        first_commit = self.first_commit_pending.get(face, True)   # for the reply only
        proposal = self._issue_pending_proposal(
            category=face, change={face: facet},
            distribution={}, evidence=list(evidence), ttl=ttl,
        )
        return {
            "status": "proposal",
            "proposal_id": proposal.proposal_id,
            "payload_to_sign": proposal.payload_to_sign,
            "first_commit": first_commit,
        }

    # ------------------------------------------------------------------
    # Proposal issuance
    # ------------------------------------------------------------------

    def _issue_pending_proposal(
        self,
        category: str,
        change: Dict[str, Any],
        distribution: Dict[str, float],
        evidence: List[str],
        ttl: float = PROPOSAL_TTL_SECONDS,
    ) -> PendingProposal:
        if category not in ALLOWED_CHARACTER_FIELDS:
            raise ValueError(f"Disallowed mutation category: {category}")
        if set(change.keys()) != {category}:          # F3
            raise ValueError(
                f"Change keys {sorted(change)} must be exactly the proposed "
                f"category {{{category!r}}}"
            )
        for k, v in change.items():
            _check_facet(v)
        change = {k: _clean_facet(v) for k, v in change.items()}

        # G1: derived from the gate, never supplied by the caller.
        first_commit = self.first_commit_pending.get(category, True)

        proposal_id = str(uuid.uuid4())
        nonce = secrets.token_hex(16)
        timestamp = time.time()
        expires_at = timestamp + ttl

        evidence_root = _sha256(_canonical_json(evidence))            # F2
        distribution_root = _sha256(_canonical_json(distribution))    # F2
        change_hash = _sha256(_canonical_json(change))

        payload_obj = {
            "schema_version": SCHEMA_VERSION,
            "kind": "mutation_proposal",
            "organism_id": self.organism_id,
            "proposal_id": proposal_id,
            "category": category,
            "change": change,
            "change_hash": change_hash,
            "evidence_root": evidence_root,
            "distribution_root": distribution_root,
            "first_commit": first_commit,
            "prior_character_root": self._character_root(),   # F4
            "prior_trace_head": self._trace_head,             # F4
            "mutation_sequence": self.mutation_sequence,      # F4
            "nonce": nonce,
            "timestamp": _fixed(timestamp),
            "expires_at": _fixed(expires_at),
        }
        payload_to_sign = _canonical_json(payload_obj)

        pending = PendingProposal(
            proposal_id=proposal_id,
            organism_id=self.organism_id,
            category=category,
            change=change,
            change_hash=change_hash,
            distribution=distribution,
            distribution_root=distribution_root,
            evidence=evidence,
            evidence_root=evidence_root,
            first_commit=first_commit,
            prior_character_root=self._character_root(),
            prior_trace_head=self._trace_head,
            mutation_sequence=self.mutation_sequence,
            nonce=nonce,
            timestamp=timestamp,
            expires_at=expires_at,
            payload_to_sign=payload_to_sign,
            payload_hash=_sha256(payload_to_sign),
        )
        self.pending[proposal_id] = pending
        self._save()          # previously missing
        return pending

    def _recompute_payload(self, p: PendingProposal) -> str:
        """Re-derived from the fields that will actually be applied and recorded."""
        return _canonical_json({
            "schema_version": SCHEMA_VERSION,
            "kind": "mutation_proposal",
            "organism_id": p.organism_id,
            "proposal_id": p.proposal_id,
            "category": p.category,
            "change": p.change,
            "change_hash": _sha256(_canonical_json(p.change)),
            "evidence_root": _sha256(_canonical_json(p.evidence)),
            "distribution_root": _sha256(_canonical_json(p.distribution)),
            "first_commit": p.first_commit,
            "prior_character_root": p.prior_character_root,
            "prior_trace_head": p.prior_trace_head,
            "mutation_sequence": p.mutation_sequence,
            "nonce": p.nonce,
            "timestamp": _fixed(p.timestamp),
            "expires_at": _fixed(p.expires_at),
        })

    # ------------------------------------------------------------------
    # External authorization — verify only
    # ------------------------------------------------------------------

    def authorize_and_apply(
        self, proposal_id: str, signature_b64: str, owner_note: str = "",
    ) -> Optional[Checkpoint]:
        """
        Returns a Checkpoint REQUEST on success (the owner must sign it and
        call install_checkpoint before the state will load again), or None
        on rejection. Fail-closed: an applied-but-unattested state is
        deliberately not loadable.
        """
        if self.public_key is None or self.organism_id is None:
            raise RuntimeError("Organism has not hatched.")

        if proposal_id not in self.pending:
            self._reject(proposal_id, "unknown or already-consumed proposal_id")
            return None

        p = self.pending[proposal_id]
        consume_key = f"{p.proposal_id}|{p.nonce}"

        if consume_key in self.consumed:
            self._reject(proposal_id, "replay of consumed proposal/nonce")
            return None
        if p.organism_id != self.organism_id:
            self._reject(proposal_id, "wrong organism_id")
            return None
        if time.time() > p.expires_at:
            self._reject(proposal_id, "proposal expired")
            return None

        # F4: the state this was read from must still be the current state.
        if p.prior_character_root != self._character_root():
            self._reject(proposal_id, "stale proposal: character has advanced since issuance")
            return None
        if p.prior_trace_head != self._trace_head:
            self._reject(proposal_id, "stale proposal: trace has advanced since issuance")
            return None
        if p.mutation_sequence != self.mutation_sequence:
            self._reject(proposal_id, "stale proposal: mutation sequence has advanced")
            return None

        # G1: the flag the owner signed must match the gate as it actually is.
        expected_fc = self.first_commit_pending.get(p.category, True)
        if p.first_commit != expected_fc:
            self._reject(
                proposal_id,
                f"first_commit flag {p.first_commit} contradicts gate state {expected_fc}",
            )
            return None

        # F3 + schema, re-checked at apply time.
        try:
            if set(p.change.keys()) != {p.category}:
                raise ValueError(f"change keys {sorted(p.change)} != category {p.category}")
            if p.category not in ALLOWED_CHARACTER_FIELDS:
                raise ValueError(f"disallowed category {p.category}")
            for k, v in p.change.items():
                _check_facet(v)
        except ValueError as e:
            self._reject(proposal_id, f"schema violation at apply time: {e}")
            return None

        # F2: evidence and distribution are re-derived, so post-signature
        # substitution changes the payload and breaks the signature.
        recomputed = self._recompute_payload(p)
        if recomputed != p.payload_to_sign:
            self._reject(proposal_id, "envelope inconsistency (evidence, distribution, or change altered)")
            return None

        try:
            self.public_key.verify(
                base64.urlsafe_b64decode(signature_b64), recomputed.encode("utf-8")
            )
        except InvalidSignature:
            self._reject(proposal_id, "invalid signature")
            return None
        except Exception:
            self._reject(proposal_id, "signature verification error")
            return None

        prior = {k: list(v) for k, v in self.character.items()}
        for k, v in p.change.items():
            # The only write to the crystal anywhere on this line: one append.
            self.character[k] = list(self.character[k]) + [_clean_facet(v)]

        self.first_commit_pending[p.category] = False
        self.consumed.add(consume_key)
        self.mutation_sequence += 1
        del self.pending[proposal_id]

        # Other outstanding proposals are now provably stale, but they are
        # deliberately NOT purged: purging them makes a replayed stale
        # proposal fail as "unknown proposal_id", which hides the real reason
        # and leaves the stale-detection branch unreachable. Keep them so the
        # rejection names the actual cause.

        record = MutationRecord(
            proposal_id=p.proposal_id, category=p.category, change=p.change,
            distribution=p.distribution, evidence=p.evidence,
            first_commit=p.first_commit, mutation_sequence=self.mutation_sequence,
            authorized_at=time.time(), signature_b64=signature_b64,
            prior_character_snapshot=prior, note=owner_note,
        )
        self._append_trace({
            "event": "authorized_mutation",
            "record": asdict(record),
            "timestamp": record.authorized_at,
        })
        self.basin = [q for q in self.basin if q.category != p.category]
        self._save()
        return self.checkpoint_request()

    def _reject(self, proposal_id: str, reason: str) -> None:
        self._append_trace({
            "event": "authorization_rejected",
            "proposal_id": proposal_id,
            "reason": reason,
            "timestamp": time.time(),
        })
        self._save()


# ===========================================================================
# OWNER SIDE — outside the organism entirely (R2: same process here)
# ===========================================================================

def owner_sign_external(private_key_pem: str, payload_to_sign: str) -> str:
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("ascii"), password=None
    )
    return base64.urlsafe_b64encode(
        private_key.sign(payload_to_sign.encode("utf-8"))
    ).decode("ascii")


class OwnerWitness:
    """
    Identity-pinned linear checkpoint chain held OUTSIDE the organism.

    This is what makes rollback detectable. The organism cannot detect its
    own rollback: a restored file carries a genuinely owner-signed older
    checkpoint and is internally valid by construction. The witness catches
    it because it remembers a sequence the restored file does not contain.

    Merged witness (v0.7). It pins the organism's birth_root, keeps the
    current/successor split, validates inside record(), and requires
    enrollment to be parentless. See MERGE_NOTES.md.

    R1 is UNCHANGED and unclosed: a local JSON file standing in for a TPM
    counter / HSM / remote notary. An attacker with write access to both
    files rolls back both. Nothing in this merge addresses that, and nothing
    in software can.
    """

    def __init__(self, ledger_path: Path | str):
        self.path = Path(ledger_path)
        self.ledger: Dict[str, Dict[str, Any]] = {}
        if self.path.exists():
            self.ledger = json.loads(self.path.read_text(encoding="utf-8"))

    def _persist(self) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(_canonical_json(self.ledger), encoding="utf-8")
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.path)

    def record(self, cp: Checkpoint) -> None:
        """
        M2: validate BEFORE writing.

        Kernel A's record() overwrote the ledger unconditionally. The split
        checks were only ever called by the audit path, so anything that
        reached record() -- including a checkpoint the witness would have
        rejected a line earlier -- became the new head. A witness that can be
        made to forget by being handed the thing it should refuse is not a
        witness. Ported from Kernel P, which called check() inside record().
        """
        self.check_successor(cp)
        self.ledger[cp.organism_id] = {
            "sequence": cp.sequence,
            "checkpoint_hash": _sha256(HumbleSeed.checkpoint_payload(cp)),
            # M1: pin identity, not just position on a chain.
            "birth_root": cp.birth_root,
        }
        self._persist()

    def _check_identity(self, cp: Checkpoint, known: Dict[str, Any]) -> None:
        """
        M1 (merged from Kernel P): pin the organism, not only the sequence.

        Kernel A's ledger held sequence and checkpoint hash and nothing that
        said WHICH organism. A fresh keypair claiming the same organism_id
        could be spliced onto an existing chain: sequence continuity held,
        parent hashes held, and the witness had no field with which to
        object. Kernel P pinned genesis_hash for exactly this reason. Here
        the pin is birth_root, which is strictly stronger -- it attests the
        whole birth record rather than the genesis hash alone.
        """
        pinned = known.get("birth_root")
        if pinned is not None and cp.birth_root != pinned:
            raise RollbackDetected(
                "Identity fork: checkpoint birth_root does not match the witness. "
                "A different organism is claiming this identity."
            )

    def check_current(self, cp: Checkpoint) -> None:
        """The state an organism presents must BE the branch we recorded."""
        known = self.ledger.get(cp.organism_id)
        if known is None:
            # I1: fail closed. An organism this witness never enrolled is not
            # a branch we recorded; it is a different organism.
            raise RollbackDetected(
                f"Unknown organism: witness has never recorded {cp.organism_id!r}. "
                f"A presented state must belong to an enrolled organism."
            )
        self._check_identity(cp, known)
        if cp.sequence < known["sequence"]:
            raise RollbackDetected(
                f"Rollback: organism presents sequence {cp.sequence}, "
                f"witness holds {known['sequence']}"
            )
        if cp.sequence > known["sequence"]:
            raise RollbackDetected(
                f"Unwitnessed advance: organism presents sequence {cp.sequence}, "
                f"witness holds {known['sequence']} — this branch was never attested here"
            )
        if _sha256(HumbleSeed.checkpoint_payload(cp)) != known["checkpoint_hash"]:
            raise RollbackDetected(
                f"Fork: a different state also claims sequence {cp.sequence}"
            )

    def check_successor(self, cp: Checkpoint) -> None:
        """
        G4: a new checkpoint must be the EXACT next link, parented to the
        one we recorded. A high-water mark alone lets an advancing fork
        with an unrelated parent overtake the real branch.
        """
        known = self.ledger.get(cp.organism_id)
        if known is None:
            if cp.sequence != 0:
                raise RollbackDetected(
                    f"Unknown organism must start at sequence 0, got {cp.sequence}"
                )
            # M4 (merged from Kernel P): enrollment must also be parentless.
            # Sequence 0 with a nonzero parent is a checkpoint claiming to
            # begin a chain while pointing at a predecessor the witness never
            # saw -- an attacker's branch presented as a birth.
            if cp.prev_checkpoint_hash != "0" * 64:
                raise RollbackDetected(
                    "Invalid enrollment: genesis checkpoint has a nonzero parent"
                )
            return
        self._check_identity(cp, known)
        if cp.sequence != known["sequence"] + 1:
            raise RollbackDetected(
                f"Non-successor checkpoint: got sequence {cp.sequence}, "
                f"expected {known['sequence'] + 1}"
            )
        if cp.prev_checkpoint_hash != known["checkpoint_hash"]:
            raise RollbackDetected(
                f"Forked parent at sequence {cp.sequence}: checkpoint is parented to "
                f"a branch this witness never recorded"
            )


class OwnerTool:
    """Convenience wrapper: sign proposals, attest state, keep the witness."""

    def __init__(self, private_key_pem: str, witness: OwnerWitness):
        self._pem = private_key_pem
        self.witness = witness

    def sign_proposal(self, payload_to_sign: str) -> str:
        return owner_sign_external(self._pem, payload_to_sign)

    def attest(self, seed: HumbleSeed, cp: Checkpoint) -> bool:
        """Check for rollback, then sign and install the checkpoint."""
        self.witness.check_successor(cp)
        sig = owner_sign_external(self._pem, HumbleSeed.checkpoint_payload(cp))
        if not seed.install_checkpoint(cp, sig):
            return False
        self.witness.record(cp)
        return True

    def owner_public_key_b64(self) -> str:
        """The key the owner actually holds — known from OUTSIDE the state file."""
        pk = serialization.load_pem_private_key(
            self._pem.encode("ascii"), password=None).public_key()
        return base64.urlsafe_b64encode(pk.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)).decode("ascii")

    def audit(self, seed: HumbleSeed, expected_organism_id: Optional[str] = None) -> bool:
        """Full external audit of a loaded organism, including rollback.

        I2: identity is pinned from outside the state before anything the
        state says about itself is believed. verify() checks the state is
        internally consistent under ITS OWN key; this checks that the key is
        OURS. Holds even when self.witness is None.
        """
        if seed.birth is None:
            raise IntegrityError("No birth record to audit")
        if seed.birth.public_key_b64 != self.owner_public_key_b64():
            raise IntegrityError(
                "Owner key mismatch: the organism's birth record names a key this "
                "owner does not hold. The state belongs to someone else."
            )
        if expected_organism_id is not None and seed.organism_id != expected_organism_id:
            raise IntegrityError(
                f"Organism mismatch: expected {expected_organism_id!r}, "
                f"state presents {seed.organism_id!r}"
            )
        seed.verify()
        if seed.checkpoint is None:
            raise IntegrityError("No checkpoint to audit")
        if self.witness is not None:
            self.witness.check_current(seed.checkpoint)
        return True
