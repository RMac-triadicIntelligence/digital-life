"""Makes the facet line from the v0.7.1 kernel source by a recorded patch. v0.7.1 itself is never edited.

Every replacement is asserted to match exactly once, so a different v0.7.1 file cannot be patched by accident.
Output: piccolo_facet_kernel_v0_1.py and FACET_KERNEL.diff (unified diff against v0.7.1).
"""
import difflib
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "vendor/kernel/humble_seed_v0_7_1.py"
V071 = "8b849cd0710c8c33a0657f09b65da71ff7bf933d9ed3e947ec27f91e297d367b"
src = SRC.read_text()
assert hashlib.sha256(src.encode()).hexdigest() == V071, "not the v0.7.1 kernel"
out = src


def swap(old, new, count=1):
    global out
    assert out.count(old) == count, (out.count(old), old[:70])
    out = out.replace(old, new)


# 1. header ---------------------------------------------------------------------------------------------
i0 = out.index('"""'); i1 = out.index('"""', i0 + 3) + 3
HEADER = '''"""
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
"""'''
out = out[:i0] + HEADER + out[i1:]

# 2. constants ------------------------------------------------------------------------------------------
swap('SCHEMA_VERSION = "0.7"', 'SCHEMA_VERSION = "piccolo-facet-0.1"')
swap('''VALUE_MIN, VALUE_MAX = 0.0, 1.0
PROPOSAL_TTL_SECONDS = 3600.0

LABEL_TO_DELTA = {"preference": -0.25}
''', '''FACET_FIELDS = ("day", "grown_from", "place")
PLACE_MAX = 65535
PROPOSAL_TTL_SECONDS = 3600.0
''')

# 3. facet checks, placed after the helpers ----------------------------------------------------------------
swap('''class IntegrityError(RuntimeError):''', '''_HEX = set("0123456789abcdef")


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


class IntegrityError(RuntimeError):''')

# 4. types ----------------------------------------------------------------------------------------------
swap("    change: Dict[str, float]\n", "    change: Dict[str, Any]\n", count=2)
swap("    prior_character_snapshot: Dict[str, float]\n", "    prior_character_snapshot: Dict[str, Any]\n")
swap("        self.character: Dict[str, float] = {}\n", "        self.character: Dict[str, List[Dict[str, Any]]] = {}\n")

# 5. constitution and birth -----------------------------------------------------------------------------
swap('''                "Mutation values are numbers in range, never interpretation labels",''',
     '''                "A mutation is exactly one facet appended to one face; never a number, never an interpretation label, never a removal or an alteration",''')
swap('''            "value_range": [VALUE_MIN, VALUE_MAX],''',
     '''            "character_form": "append_only_facets",
            "facet_fields": list(FACET_FIELDS),''')
swap('''        self.character = {"verbosity": 0.5, "formality": 0.5, "curiosity": 0.6}''',
     '''        self.character = {k: [] for k in sorted(ALLOWED_CHARACTER_FIELDS)}   # born with three empty faces''')

# 6. verify ---------------------------------------------------------------------------------------------
swap('''        for k, v in self.character.items():
            if k not in ALLOWED_CHARACTER_FIELDS:
                raise IntegrityError(f"Character contains disallowed field: {k}")
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise IntegrityError(f"Character field {k} is not numeric: {type(v).__name__}")
            if not (VALUE_MIN <= float(v) <= VALUE_MAX):
                raise IntegrityError(f"Character field {k} out of range: {v}")
''', '''        if set(self.character.keys()) != ALLOWED_CHARACTER_FIELDS:
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
''')

# 7. the interpreter goes; dwell() and propose_facet() come in ----------------------------------------------
j0 = out.index("    # ------------------------------------------------------------------\n    # Interpretation + basin\n")
j1 = out.index("    # ------------------------------------------------------------------\n    # Proposal issuance\n")
NEWSEC = '''    # ------------------------------------------------------------------
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

'''
out = out[:j0] + NEWSEC + out[j1:]

# 8. issue ----------------------------------------------------------------------------------------------
swap('''        for k, v in change.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ValueError(
                    f"Mutation value for {k} must be a number, got {type(v).__name__}"
                )
            if not (VALUE_MIN <= float(v) <= VALUE_MAX):
                raise ValueError(
                    f"Mutation value for {k} out of range [{VALUE_MIN}, {VALUE_MAX}]: {v}"
                )
        change = {k: float(v) for k, v in change.items()}
''', '''        for k, v in change.items():
            _check_facet(v)
        change = {k: _clean_facet(v) for k, v in change.items()}
''')

# 9. apply ----------------------------------------------------------------------------------------------
swap('''            for k, v in p.change.items():
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    raise ValueError(f"non-numeric value for {k}")
                if not (VALUE_MIN <= float(v) <= VALUE_MAX):
                    raise ValueError(f"out-of-range value for {k}")
''', '''            for k, v in p.change.items():
                _check_facet(v)
''')
swap('''        prior = dict(self.character)
        for k, v in p.change.items():
            self.character[k] = float(v)
''', '''        prior = {k: list(v) for k, v in self.character.items()}
        for k, v in p.change.items():
            # The only write to the crystal anywhere on this line: one append.
            self.character[k] = list(self.character[k]) + [_clean_facet(v)]
''')

# 10. v0.7.1's built-in harness mutates numbers; it is cut. Tests for this line are separate files. -----------
k0 = out.index("# ---------------------------------------------------------------------------\n# Falsification harness\n")
out = out[:k0].rstrip() + "\n"

for gone in ("VALUE_MIN", "VALUE_MAX", "LABEL_TO_DELTA", "dwell_or_propose", "interpret(", "float(v)"):
    assert gone not in out, gone
compile(out, "piccolo_facet_kernel_v0_1.py", "exec")
(HERE / "piccolo_facet_kernel_v0_1.py").write_text(out)
diff = "".join(difflib.unified_diff(src.splitlines(True), out.splitlines(True),
                                    "humble_seed_v0_7_1.py", "piccolo_facet_kernel_v0_1.py", n=2))
(HERE / "FACET_KERNEL.diff").write_text(diff)
print("facet kernel", hashlib.sha256(out.encode()).hexdigest(), len(out.splitlines()), "lines")
print("v0.7.1 untouched", hashlib.sha256(SRC.read_bytes()).hexdigest() == V071)
