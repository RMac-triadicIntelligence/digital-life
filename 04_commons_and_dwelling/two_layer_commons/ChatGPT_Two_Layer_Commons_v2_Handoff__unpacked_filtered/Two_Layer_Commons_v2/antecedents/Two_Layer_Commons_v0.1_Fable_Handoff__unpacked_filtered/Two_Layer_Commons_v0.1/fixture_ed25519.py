"""RFC 8032 arithmetic used only with reproducible, public research keys."""
import hashlib

P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, -1, P) % P
SQRT_NEG1 = pow(2, (P - 1) // 4, P)
IDENTITY = (0, 1, 1, 0)


def decode(encoded):
    if len(encoded) != 32:
        raise ValueError("point length")
    value = int.from_bytes(encoded, "little")
    y = value & (2**255 - 1)
    if y >= P:
        raise ValueError("noncanonical point")
    u = (y * y - 1) % P
    v = (D * y * y + 1) % P
    x = u * pow(v, 3, P) * pow(u * pow(v, 7, P), (P - 5) // 8, P) % P
    if (v * x * x - u) % P:
        x = x * SQRT_NEG1 % P
    if (v * x * x - u) % P or (x == 0 and value >> 255):
        raise ValueError("invalid point")
    if x % 2 != value >> 255:
        x = -x % P
    return x, y, 1, x * y % P


def encode(point):
    x, y, z, _ = point
    inverse = pow(z, -1, P)
    return ((y * inverse % P) | ((x * inverse % P & 1) << 255)).to_bytes(32, "little")


BASE = decode((4 * pow(5, -1, P) % P).to_bytes(32, "little"))


def add(p, q):
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % P
    b = (y1 + x1) * (y2 + x2) % P
    c = 2 * D * t1 * t2 % P
    d = 2 * z1 * z2 % P
    return (b - a) * (d - c) % P, (d + c) * (a + b) % P, (d - c) * (d + c) % P, (b - a) * (a + b) % P


def multiply(point, scalar):
    result = IDENTITY
    while scalar:
        if scalar & 1:
            result = add(result, point)
        point = add(point, point)
        scalar >>= 1
    return result


def hashed(data):
    return int.from_bytes(hashlib.sha512(data).digest(), "little")


class InvalidSignature(Exception):
    pass


class PublicKey:
    def __init__(self, raw):
        point = decode(raw)
        if encode(multiply(point, 8)) == encode(IDENTITY) or encode(multiply(point, L)) != encode(IDENTITY):
            raise ValueError("public key outside prime-order subgroup")
        self.raw, self.point = raw, point

    @classmethod
    def from_public_bytes(cls, raw):
        return cls(raw)

    def public_bytes(self, **_):
        return self.raw

    def verify(self, signature, message):
        if len(signature) != 64:
            raise InvalidSignature()
        encoded_r = signature[:32]
        s = int.from_bytes(signature[32:], "little")
        try:
            r = decode(encoded_r)
        except ValueError as error:
            raise InvalidSignature() from error
        if s >= L:
            raise InvalidSignature()
        k = hashed(encoded_r + self.raw + message) % L
        if encode(multiply(BASE, s)) != encode(add(r, multiply(self.point, k))):
            raise InvalidSignature()


class PrivateKey:
    def __init__(self, seed):
        expanded = hashlib.sha512(seed).digest()
        self.scalar = (int.from_bytes(expanded[:32], "little") & (2**254 - 8)) | 2**254
        self.prefix = expanded[32:]
        self.public = PublicKey(encode(multiply(BASE, self.scalar)))
        self.seed = seed

    def public_key(self):
        return self.public

    def private_bytes(self, **_):
        return self.seed.hex().encode("ascii")

    def sign(self, message):
        r = hashed(self.prefix + message) % L
        encoded_r = encode(multiply(BASE, r))
        k = hashed(encoded_r + self.public.raw + message) % L
        return encoded_r + ((r + k * self.scalar) % L).to_bytes(32, "little")
