"""Execute the archived kernel with deterministic, test-only system services."""
import ast
import hashlib
import sys
import uuid
from pathlib import Path
from types import ModuleType, SimpleNamespace

from fixture_ed25519 import InvalidSignature, PrivateKey, PublicKey

SOURCE_HASH = "08a756043a6500fcda85fc2795471b4e8659de5364424c035aa5c6aa91cb3707"


class FixtureServices:
    def __init__(self):
        self.label = ""
        self.tick = 0
        self.sequence = 0

    def start(self, label):
        self.label, self.tick, self.sequence = label, 0, 0

    def draw(self, domain):
        self.sequence += 1
        return hashlib.sha256(f"PUBLIC COMMONS FIXTURE/{self.label}/{domain}/{self.sequence}".encode()).digest()

    def key(self):
        return PrivateKey(self.draw("key"))

    def uuid(self):
        return uuid.UUID(bytes=self.draw("identity")[:16], version=4)

    def nonce(self, size):
        return self.draw("nonce")[:size].hex()

    def time(self):
        return 1_800_000_000.0 + self.tick


def load_kernel():
    path = Path(__file__).with_name("vendor") / "humble_seed_v0_7.py"
    original = path.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_HASH:
        raise RuntimeError("canonical source bytes changed")
    tree = ast.parse(original, filename=str(path))
    replaced = {"cryptography.hazmat.primitives.asymmetric.ed25519",
                "cryptography.hazmat.primitives", "cryptography.exceptions"}
    tree.body = [
        node for node in tree.body
        if not (isinstance(node, ast.ImportFrom) and node.module in replaced)
        and not (isinstance(node, ast.Import) and node.names[0].name in {"uuid", "time", "secrets"})
    ]
    services = FixtureServices()
    module = ModuleType("_commons_humble_seed_v07")
    sys.modules[module.__name__] = module
    module.__dict__.update(
        Ed25519PrivateKey=SimpleNamespace(generate=services.key),
        Ed25519PublicKey=PublicKey,
        InvalidSignature=InvalidSignature,
        serialization=SimpleNamespace(
            Encoding=SimpleNamespace(PEM="fixture", Raw="raw"),
            PrivateFormat=SimpleNamespace(PKCS8="fixture"),
            PublicFormat=SimpleNamespace(Raw="raw"),
            NoEncryption=lambda: None,
            load_pem_private_key=lambda data, password: PrivateKey(bytes.fromhex(data.decode("ascii"))),
        ),
        uuid=SimpleNamespace(uuid4=services.uuid),
        secrets=SimpleNamespace(token_hex=services.nonce),
        time=SimpleNamespace(time=services.time),
    )
    exec(compile(tree, filename=str(path), mode="exec"), module.__dict__)
    return module, services


class Constitution:
    """Host-only kernel handle. Body and choice receive neither it nor its keys."""

    def __init__(self, kernel, services, directory, subject):
        services.start(subject)
        self.services = services
        self.seed = kernel.HumbleSeed(directory / "seed")
        _, private, checkpoint = self.seed.hatch()
        self.signer = PrivateKey(bytes.fromhex(private))
        self.witness = kernel.OwnerWitness(directory / "witness.json")
        self.attest(checkpoint)
        self.seed.verify()
        self.witness.check_current(self.seed.checkpoint)

    def attest(self, checkpoint):
        self.witness.check_successor(checkpoint)
        payload = self.seed.checkpoint_payload(checkpoint)
        if not self.seed.install_checkpoint(checkpoint, self.sign(payload)):
            raise RuntimeError("test owner checkpoint rejected")
        self.witness.record(checkpoint)

    def sign(self, payload):
        import base64
        return base64.urlsafe_b64encode(self.signer.sign(payload.encode("utf-8"))).decode("ascii")
