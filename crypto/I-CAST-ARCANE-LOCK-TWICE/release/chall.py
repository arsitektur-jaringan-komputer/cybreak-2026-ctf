from hashlib import sha256
from os import urandom
from secrets import randbelow

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


BITS = 18


def key(x):
    return sha256(x.to_bytes(3, "big")).digest()[:16]


def enc(m, a, b):
    iv1, iv2 = urandom(16), urandom(16)
    n = 16 - len(m) % 16
    m += bytes([n]) * n

    f = Cipher(algorithms.AES(key(a)), modes.CBC(iv1)).encryptor()
    c = f.update(m) + f.finalize()
    g = Cipher(algorithms.AES(key(b)), modes.CBC(iv2)).encryptor()
    c = g.update(c) + g.finalize()

    return {"iv1": iv1.hex(), "iv2": iv2.hex(), "ct": c.hex()}


if __name__ == "__main__":
    flag = b"CYB26{REDACTED}"
    a, b = randbelow(1 << BITS), randbelow(1 << BITS)
    while a == b:
        b = randbelow(1 << BITS)

    msg = b"Rudy and Seria test their locks before sealing the secret scroll."

    print("bits =", BITS)
    print("msg =", repr(msg))
    print("sample =", enc(msg, a, b))
    print("target =", enc(flag, a, b))
