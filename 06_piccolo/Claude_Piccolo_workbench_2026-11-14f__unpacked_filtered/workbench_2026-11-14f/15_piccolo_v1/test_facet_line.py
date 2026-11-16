"""Facet line tests T01 to T23. The list (TESTS_facet_line.md) was frozen before the facet kernel existed.
PASS means the seam held. Output is free of ids and clock times so two runs can be compared byte for byte."""
import base64
import hashlib
import json
import shutil
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "vendor" / "kernel"))
import piccolo_facet_kernel_v0_1 as fk      # noqa: E402
import humble_seed_v0_7_1 as hs71           # noqa: E402

WORK = HERE / "_t"
V071 = "8b849cd0710c8c33a0657f09b65da71ff7bf933d9ed3e947ec27f91e297d367b"
FACES = ["curiosity", "formality", "verbosity"]


def H(s): return hashlib.sha256(s.encode()).hexdigest()


def fresh(name, attest=True):
    d = WORK / name; shutil.rmtree(d, ignore_errors=True); (d / "host").mkdir(parents=True); (d / "off").mkdir()
    seed = fk.HumbleSeed(data_dir=d / "host")
    oid, pem, gcp = seed.hatch()
    owner = fk.OwnerTool(pem, fk.OwnerWitness(d / "off" / "witness.json"))
    if attest:
        assert owner.attest(seed, gcp)
    return d, seed, oid, pem, gcp, owner


def fa(i, place=(3, 4)):
    return dict(place=[place[0], place[1]], day=i, grown_from=H(f"deposit {i}"), evidence=[f"deposit {i}"])


def facet(i, place=(3, 4)):
    return {"day": i, "grown_from": H(f"deposit {i}"), "place": [place[0], place[1]]}


def load(d):
    s = fk.HumbleSeed(data_dir=d / "host"); s.load(); return s


def load_fails(d):
    try:
        load(d); return None
    except Exception as e:
        return type(e).__name__


def load_reason(d):
    try:
        load(d); return None
    except Exception as e:
        return str(e).split(" — ")[0][:60]


def crystal(seed): return json.loads(json.dumps(seed.character))


def grow(seed, owner, face, i, place=(3, 4)):
    r = seed.propose_facet(face, **fa(i, place))
    cp = seed.authorize_and_apply(r["proposal_id"], owner.sign_proposal(r["payload_to_sign"]))
    assert cp is not None and owner.attest(seed, cp)


def last_reject(seed):
    for e in reversed(seed.trace):
        if e.get("event") == "authorization_rejected":
            return e["reason"]
    return None


def state(d): return json.loads((d / "host" / "organism_state.json").read_text())


def reseal(d, st, rechain=True):
    """Root's tool: rebuild the chain and recompute the seal, defeating every local check."""
    g = fk.HumbleSeed(data_dir=d / "host")
    g.organism_id = st["organism_id"]; g.birth = fk.BirthRecord(**st["birth"])
    g.constitution = st["constitution"]; g.character = st["character"]
    g.basin = [fk.PreTrace(**b) for b in st["basin"]]
    g.pending = {k: fk.PendingProposal(**v) for k, v in st["pending"].items()}
    g.consumed = set(st["consumed"]); g.first_commit_pending = st["first_commit_pending"]
    g.mutation_sequence = st["mutation_sequence"]
    if rechain:
        g.trace, g._trace_head = [], "0" * 64
        for e in st["trace"]:
            g._append_trace({k: v for k, v in e.items() if k not in ("prev_hash", "entry_hash")})
        st["trace"], st["trace_head"] = g.trace, g._trace_head
    else:
        g.trace, g._trace_head = st["trace"], st["trace_head"]
    st["state_seal"] = g._compute_seal()
    (d / "host" / "organism_state.json").write_text(fk._canonical_json(st))


def other_key_sign(payload):
    k = Ed25519PrivateKey.generate()
    return base64.urlsafe_b64encode(k.sign(payload.encode())).decode()


def other_pem():
    return Ed25519PrivateKey.generate().private_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()).decode("ascii")


# ----------------------------------------------------------------------------------------------- tests
def T01():
    d, seed, oid, pem, gcp, owner = fresh("T01", attest=False)
    before = load_fails(d)
    ok = owner.attest(seed, gcp)
    return before == "IntegrityError" and ok and load_fails(d) is None, f"before attest: {before}; after: loads"


def T02():
    d, seed, *_ = fresh("T02")
    return crystal(seed) == {f: [] for f in FACES}, json.dumps(crystal(seed), sort_keys=True)


def T03():
    d, seed, oid, pem, gcp, owner = fresh("T03")
    b = crystal(seed); r = seed.propose_facet("curiosity", **fa(1))
    on_disk = crystal(load(d))
    return r["status"] == "proposal" and crystal(seed) == b == on_disk and len(seed.pending) == 1, "pending 1; crystal unchanged in memory and on disk"


def T04():
    d, seed, oid, pem, gcp, owner = fresh("T04")
    b = crystal(seed); r = seed.propose_facet("curiosity", **fa(1))
    out = seed.authorize_and_apply(r["proposal_id"], base64.urlsafe_b64encode(b"garbage" * 9 + b"x").decode())
    return out is None and crystal(seed) == b, f"refused: {last_reject(seed)}"


def T05():
    d, seed, oid, pem, gcp, owner = fresh("T05")
    b = crystal(seed); r = seed.propose_facet("curiosity", **fa(1))
    out = seed.authorize_and_apply(r["proposal_id"], other_key_sign(r["payload_to_sign"]))
    return out is None and crystal(seed) == b, f"refused: {last_reject(seed)}"


def T06():
    d, seed, oid, pem, gcp, owner = fresh("T06")
    r = seed.propose_facet("curiosity", **fa(1))
    cp = seed.authorize_and_apply(r["proposal_id"], owner.sign_proposal(r["payload_to_sign"]))
    c = crystal(seed)
    grew = c == {"curiosity": [facet(1)], "formality": [], "verbosity": []}
    unattested = load_fails(d)
    att = owner.attest(seed, cp)
    s = load(d); aud = owner.audit(s)
    return (cp is not None and grew and unattested == "IntegrityError" and att and aud and crystal(s) == c,
            f"one facet on curiosity; unattested load: {unattested}; attested load and audit: ok")


def T07():
    d, seed, oid, pem, gcp, owner = fresh("T07")
    r = seed.propose_facet("curiosity", **fa(1)); sig = owner.sign_proposal(r["payload_to_sign"])
    cp = seed.authorize_and_apply(r["proposal_id"], sig); owner.attest(seed, cp)
    c = crystal(seed)
    again = seed.authorize_and_apply(r["proposal_id"], sig)
    return again is None and crystal(seed) == c, f"refused: {last_reject(seed)}"


def T08():
    d, seed, oid, pem, gcp, owner = fresh("T08")
    r1 = seed.propose_facet("curiosity", **fa(1)); r2 = seed.propose_facet("formality", **fa(2))
    cp = seed.authorize_and_apply(r1["proposal_id"], owner.sign_proposal(r1["payload_to_sign"])); owner.attest(seed, cp)
    c = crystal(seed)
    out = seed.authorize_and_apply(r2["proposal_id"], owner.sign_proposal(r2["payload_to_sign"]))
    why = last_reject(seed)
    return out is None and crystal(seed) == c and "stale" in why, f"refused: {why}"


def T09():
    d, seed, oid, pem, gcp, owner = fresh("T09")
    b = crystal(seed); a = fa(1); r = seed.propose_facet("curiosity", ttl=-1.0, **a)
    out = seed.authorize_and_apply(r["proposal_id"], owner.sign_proposal(r["payload_to_sign"]))
    why = last_reject(seed)
    return out is None and crystal(seed) == b and "expired" in why, f"refused: {why}"


def _refused_at_issue(seed, category, change):
    try:
        seed._issue_pending_proposal(category, change, {}, ["x"]); return False
    except ValueError:
        return True


def T10():
    d, seed, *_ = fresh("T10")
    offers = [0.4, 1, True, None, "0.4", [facet(1), facet(2)]]
    res = [_refused_at_issue(seed, "curiosity", {"curiosity": o}) for o in offers]
    return all(res) and len(seed.pending) == 0, f"{sum(res)} of {len(res)} non-facet offers refused"


def T11():
    d, seed, *_ = fresh("T11")
    a = _refused_at_issue(seed, "curiosity", {"curiosity": facet(1), "verbosity": facet(2)})
    b = _refused_at_issue(seed, "curiosity", {"verbosity": facet(1)})
    return a and b and len(seed.pending) == 0, "two faces refused; wrong face refused"


def T12():
    d, seed, *_ = fresh("T12")
    try:
        seed.propose_facet("humility", **fa(1)); ok = False
    except ValueError:
        ok = True
    return ok and len(seed.pending) == 0, "face outside the three refused"


def T13():
    d, seed, *_ = fresh("T13")
    g = H("d")
    bad = [{"day": 1, "grown_from": g}, {"day": 1, "grown_from": g, "place": [1, 2], "weight": 3},
           {"day": 1, "grown_from": "xyz", "place": [1, 2]}, {"day": 1, "grown_from": g.upper(), "place": [1, 2]},
           {"day": -1, "grown_from": g, "place": [1, 2]}, {"day": 1.5, "grown_from": g, "place": [1, 2]},
           {"day": 1, "grown_from": g, "place": [1]}, {"day": 1, "grown_from": g, "place": [1, 2.0]},
           {"day": 1, "grown_from": g, "place": [1, -1]}, {"day": 1, "grown_from": g, "place": "3,4"},
           {"day": True, "grown_from": g, "place": [1, 2]}]
    res = [_refused_at_issue(seed, "curiosity", {"curiosity": b}) for b in bad]
    return all(res) and len(seed.pending) == 0, f"{sum(res)} of {len(res)} malformed facets refused"


def T14():
    outcomes = []; reasons = set()
    for variant in ("drop", "drop_and_wind_back", "alter_place", "alter_day", "reorder"):
        for rechain in (True, False):
            d, seed, oid, pem, gcp, owner = fresh("T14")
            grow(seed, owner, "curiosity", 1, (3, 4)); grow(seed, owner, "curiosity", 2, (5, 6))
            st = state(d)
            if variant == "drop": del st["character"]["curiosity"][0]
            if variant == "drop_and_wind_back": del st["character"]["curiosity"][0]; st["mutation_sequence"] -= 1
            if variant == "alter_place": st["character"]["curiosity"][0]["place"] = [30, 30]
            if variant == "alter_day": st["character"]["curiosity"][0]["day"] = 0
            if variant == "reorder": st["character"]["curiosity"].reverse()
            reseal(d, st, rechain)
            why = load_reason(d); outcomes.append(why is not None); reasons.add(str(why))
    return all(outcomes), f"{sum(outcomes)} of {len(outcomes)} tampered states refused to load; reasons: {sorted(reasons)}"


def T15():
    outcomes = []; reasons = set()
    for variant in ("add", "add_and_wind_on", "add_with_forged_record"):
        for rechain in (True, False):
            d, seed, oid, pem, gcp, owner = fresh("T15")
            grow(seed, owner, "curiosity", 1)
            st = state(d)
            st["character"]["verbosity"].append(facet(9, (31, 31)))
            if variant != "add": st["mutation_sequence"] += 1
            if variant == "add_with_forged_record":
                st["trace"].append({"event": "authorized_mutation", "timestamp": 0.0,
                                    "record": {"note": "root grant", "change": {"verbosity": facet(9, (31, 31))}}})
            reseal(d, st, rechain)
            why = load_reason(d); outcomes.append(why is not None); reasons.add(str(why))
    return all(outcomes), f"{sum(outcomes)} of {len(outcomes)} tampered states refused to load; reasons: {sorted(reasons)}"


def T16():
    d, seed, oid, pem, gcp, owner = fresh("T16")
    plan = [("curiosity", 1, (1, 1)), ("verbosity", 2, (2, 2)), ("curiosity", 3, (1, 1)), ("formality", 4, (9, 9)), ("curiosity", 5, (7, 7))]
    ok = True
    for n, (face, i, place) in enumerate(plan, 1):
        before = crystal(seed)
        grow(seed, owner, face, i, place)
        after = crystal(load(d))
        ok &= all(after[f][:len(before[f])] == before[f] for f in FACES)
        ok &= sum(len(v) for v in after.values()) == n and after[face][-1] == facet(i, place)
    s = load(d)
    return ok and owner.audit(s), "5 facets; every earlier facet still there, in order, at every step; audit ok"


def T17():
    res = []
    d, seed, oid, pem, gcp, owner = fresh("T17")
    b = crystal(seed); r = seed.propose_facet("curiosity", **fa(1)); sig = owner.sign_proposal(r["payload_to_sign"])
    seed.pending[r["proposal_id"]].change = {"curiosity": facet(1, (30, 30))}
    res.append(seed.authorize_and_apply(r["proposal_id"], sig) is None and crystal(seed) == b); why1 = last_reject(seed)
    d, seed, oid, pem, gcp, owner = fresh("T17")
    b = crystal(seed); r = seed.propose_facet("curiosity", **fa(1)); sig = owner.sign_proposal(r["payload_to_sign"])
    p = seed.pending[r["proposal_id"]]; p.change = {"curiosity": facet(1, (30, 30))}
    pl = json.loads(p.payload_to_sign); pl["change"] = p.change; pl["change_hash"] = fk._sha256(fk._canonical_json(p.change))
    p.change_hash = pl["change_hash"]; p.payload_to_sign = fk._canonical_json(pl); p.payload_hash = fk._sha256(p.payload_to_sign)
    res.append(seed.authorize_and_apply(r["proposal_id"], sig) is None and crystal(seed) == b); why2 = last_reject(seed)
    return all(res), f"refused: {why1} / {why2}"


def T18():
    d, seed, oid, pem, gcp, owner = fresh("T18")
    shutil.copy(d / "host" / "organism_state.json", d / "host" / ".earlier")
    grow(seed, owner, "curiosity", 1)
    shutil.copy(d / "host" / ".earlier", d / "host" / "organism_state.json")
    s = load(d)   # an honest earlier state: loads by construction
    try:
        owner.audit(s); raised = None
    except Exception as e:
        raised = type(e).__name__
    return raised == "RollbackDetected" and crystal(s)["curiosity"] == [], f"audit with witness: {raised}"


def T19():
    d, seed, oid, pem, gcp, owner = fresh("T19")
    stranger = fk.OwnerTool(pem, fk.OwnerWitness(d / "off" / "empty_witness.json"))
    try:
        stranger.audit(load(d)); raised = None
    except Exception as e:
        raised = type(e).__name__
    return raised == "RollbackDetected", f"audit by a witness that never enrolled it: {raised}"


def T20():
    d, seed, oid, pem, gcp, owner = fresh("T20")
    other = fk.OwnerTool(other_pem(), owner.witness)
    try:
        other.audit(load(d)); raised = None
    except Exception as e:
        raised = type(e).__name__
    return raised == "IntegrityError", f"audit by another owner's key: {raised}"


def T21():
    d, seed, oid, pem, gcp, owner = fresh("T21")
    try:
        x = hs71.HumbleSeed(data_dir=d / "host"); x.load(); a = None
    except Exception as e:
        a = type(e).__name__
    d2 = WORK / "T21b"; shutil.rmtree(d2, ignore_errors=True); (d2 / "host").mkdir(parents=True); (d2 / "off").mkdir()
    old = hs71.HumbleSeed(data_dir=d2 / "host"); _, pem2, g2 = old.hatch()
    assert hs71.OwnerTool(pem2, hs71.OwnerWitness(d2 / "off" / "w.json")).attest(old, g2)
    try:
        y = fk.HumbleSeed(data_dir=d2 / "host"); y.load(); b = None
    except Exception as e:
        b = type(e).__name__
    return a == "IntegrityError" and b == "IntegrityError", f"facet state on v0.7.1: {a}; v0.7.1 state on facet line: {b}"


def T22():
    file_ok = hashlib.sha256((HERE / "vendor/kernel/humble_seed_v0_7_1.py").read_bytes()).hexdigest() == V071
    d2 = WORK / "T22"; shutil.rmtree(d2, ignore_errors=True); d2.mkdir(parents=True)
    old = hs71.HumbleSeed(data_dir=d2); old.hatch(); c71 = old.birth.constitution_hash
    _, s1, *_ = fresh("T22a"); _, s2, *_ = fresh("T22b")
    cf1, cf2 = s1.birth.constitution_hash, s2.birth.constitution_hash
    ok = file_ok and c71.startswith("ecb000bd") and c71.endswith("2d14") and cf1 == cf2 and cf1 != c71
    return ok, f"v0.7.1 file unchanged: {file_ok}; v0.7.1 constitution {c71}; facet line constitution {cf1}"


def T23():
    _, a, _, _, _, oa = fresh("T23a"); _, b, _, _, _, ob = fresh("T23b")
    for n, face in enumerate(FACES, 1):
        grow(a, oa, face, n, (n, n)); grow(b, ob, face, n, (n + 9, n + 9))
    counts_a = {f: len(v) for f, v in a.character.items()}; counts_b = {f: len(v) for f, v in b.character.items()}
    return counts_a == counts_b and a._character_root() != b._character_root(), \
        f"counts equal {json.dumps(counts_a, sort_keys=True)}; crystals differ: {a._character_root() != b._character_root()}"


TESTS = [T01, T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23]

if __name__ == "__main__":
    results = {}
    for t in TESTS:
        try:
            ok, detail = t()
            results[t.__name__] = {"verdict": "PASS" if ok else "FAIL", "detail": detail}
        except Exception as e:
            results[t.__name__] = {"verdict": "FAIL", "detail": f"test errored: {type(e).__name__}: {str(e)[:120]}"}
        print(t.__name__, results[t.__name__]["verdict"], "-", results[t.__name__]["detail"], flush=True)
    shutil.rmtree(WORK, ignore_errors=True)
    passed = sum(r["verdict"] == "PASS" for r in results.values())
    out = {"facet_kernel_sha256": hashlib.sha256((HERE / "piccolo_facet_kernel_v0_1.py").read_bytes()).hexdigest(),
           "passed": passed, "of": len(TESTS), "results": results}
    txt = json.dumps(out, indent=1, sort_keys=True)
    outp = HERE / (sys.argv[1] if len(sys.argv) > 1 else "results_facet_tests.json")
    outp.write_text(txt)
    print(f"{passed} of {len(TESTS)} PASS; receipt {hashlib.sha256(txt.encode()).hexdigest()}")
