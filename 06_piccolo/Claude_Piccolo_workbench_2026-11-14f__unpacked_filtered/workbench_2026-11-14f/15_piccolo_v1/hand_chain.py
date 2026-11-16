"""Piccolo v1, Part 3: one member, one chain, by hand.

From century seed 0: the lowest-numbered member alive on day 36,500. Its first deposit of each kind becomes a
facet proposal on the facet line; a bench owner key signs; the result is attested, reloaded and audited.

The owner key is a bench key made here. The keel has signed nothing. This shows the path
deposit -> proposal -> signature -> crystal -> audit with real data. It does not show which deposits ought
to become proposals (PREREG hole H9), and the facets change nothing the member does (hole H11).
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import piccolo_facet_kernel_v0_1 as fk   # noqa: E402

KIND = [("curiosity", "cur", "ranging found food on ground the family did not know"),
        ("verbosity", "tel", "kin came and witnessed what this member laid out"),
        ("formality", "tru", "the ground was as the family said")]


def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":"))


def main(src="century/seed_00.json", out="results_hand_chain.json"):
    raw = (HERE / src).read_bytes()
    src_sha = hashlib.sha256(raw).hexdigest()
    d = json.loads(raw)
    alive = sorted(d["members_alive"], key=lambda m: m["id"])
    if not alive:
        txt = json.dumps({"verdict": "NO MEMBER ALIVE", "source_sha256": src_sha}, indent=1, sort_keys=True)
        (HERE / out).write_text(txt); print(txt); return
    m = alive[0]
    work = HERE / "_hand"; shutil.rmtree(work, ignore_errors=True); (work / "host").mkdir(parents=True); (work / "off").mkdir()
    seed = fk.HumbleSeed(data_dir=work / "host")
    oid, pem, gcp = seed.hatch()
    owner = fk.OwnerTool(pem, fk.OwnerWitness(work / "off" / "witness.json"))
    assert owner.attest(seed, gcp)
    steps = []
    for face, key, words in KIND:
        first = m["first"][key]
        if first is None:
            steps.append({"face": face, "deposit": None, "facet": None, "applied": False, "why": "this member has no deposit of this kind"})
            continue
        tick, x, y, val = first
        deposit = {"source_sha256": src_sha, "seed": d["seed"], "member": m["id"], "kind": face, "what_happened": words,
                   "tick": tick, "day": tick // d["ticks_per_day"], "place": [x, y], "value": val}
        grown_from = hashlib.sha256(canon(deposit).encode()).hexdigest()
        before = json.loads(json.dumps(seed.character))
        r = seed.propose_facet(face, [x, y], deposit["day"], grown_from, [canon(deposit)])
        unsigned_changed_nothing = json.loads(json.dumps(seed.character)) == before
        cp = seed.authorize_and_apply(r["proposal_id"], owner.sign_proposal(r["payload_to_sign"]))
        applied = cp is not None and owner.attest(seed, cp)
        steps.append({"face": face, "deposit": deposit, "facet": {"day": deposit["day"], "grown_from": grown_from, "place": [x, y]},
                      "first_commit_flag": r["first_commit"], "unsigned_changed_nothing": unsigned_changed_nothing, "applied": bool(applied)})
    fresh = fk.HumbleSeed(data_dir=work / "host"); fresh.load()
    audited = owner.audit(fresh, expected_organism_id=oid)
    res = {"build": "piccolo_v1/hand_chain", "source": src, "source_sha256": src_sha,
           "member": {k: m[k] for k in ("id", "lineage", "born", "scout", "household", "obs", "cur", "tel", "tru", "nothing", "grace")},
           "member_born_day": m["born"] // d["ticks_per_day"],
           "steps": steps, "crystal": fresh.character, "crystal_root": fresh._character_root(),
           "constitution_hash": fresh.birth.constitution_hash, "signed_mutations": fresh.mutation_sequence,
           "loads": True, "audits": bool(audited),
           "owner": "bench key made by this script; the keel has signed nothing",
           "verdict": "PASS" if audited and all(s["applied"] for s in steps) else "PARTIAL"}
    shutil.rmtree(work, ignore_errors=True)
    txt = json.dumps(res, indent=1, sort_keys=True)
    (HERE / out).write_text(txt)
    print(res["verdict"], "member", m["id"], "crystal_root", res["crystal_root"], "receipt", hashlib.sha256(txt.encode()).hexdigest())


if __name__ == "__main__":
    main(*sys.argv[1:])
