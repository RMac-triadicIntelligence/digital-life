"""Observer-side deterministic evidence. Stores here never feed back to actors."""

import hashlib
import json
from pathlib import Path

ROW_CAPACITY = 100
MAX_RESULT_BYTES = 18_000_000


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def log(row, actor, layer, place, process, **data):
    assert len(row["events"]) < ROW_CAPACITY
    row["events"].append({"actor": actor, "layer": layer, "place": place, "process": process, **data})


def state_changes(row, actor, layer, place, prefix, before, after, **attributes):
    for field in before:
        if before[field] != after[field]:
            log(row, actor, layer, place, f"{prefix}.{field}", before=before[field],
                after=after[field], **attributes)


def dump(path, value):
    encoded = (canonical(value) + "\n").encode()
    if len(encoded) > MAX_RESULT_BYTES:
        raise ValueError("observer output exceeds the protocol's per-file capacity")
    path.write_bytes(encoded)
    return digest(encoded)


def matching_manifest(folder):
    folder = Path(folder)
    actual = {}
    for line in (folder / "SHA256SUMS").read_text().splitlines():
        claimed, name = line.split()
        if name in actual or Path(name).name != name:
            raise ValueError("malformed results manifest")
        observed = digest((folder / name).read_bytes())
        if claimed != observed:
            raise ValueError(f"result hash mismatch for {name}")
        actual[name] = observed
    if actual.keys() != {path.name for path in folder.glob("*.json")}:
        raise ValueError("unlisted result file")
    return actual
