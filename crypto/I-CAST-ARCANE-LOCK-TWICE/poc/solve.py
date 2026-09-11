#!/usr/bin/env python3

import ast
import sys
from hashlib import sha256
from pathlib import Path
from time import perf_counter

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


def key(x):
    return sha256(x.to_bytes(3, "big")).digest()[:16]


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def dec(data, a, b):
    iv1 = bytes.fromhex(data["iv1"])
    iv2 = bytes.fromhex(data["iv2"])
    c = bytes.fromhex(data["ct"])

    f = Cipher(algorithms.AES(key(b)), modes.CBC(iv2)).decryptor()
    c = f.update(c) + f.finalize()
    g = Cipher(algorithms.AES(key(a)), modes.CBC(iv1)).decryptor()
    m = g.update(c) + g.finalize()
    unpad = PKCS7(128).unpadder()
    return unpad.update(m) + unpad.finalize()


def recover(bits, msg, sample):
    if not 1 <= bits <= 24 or len(msg) < 16:
        raise ValueError("unsupported seed size or short calibration message")

    iv1 = bytes.fromhex(sample["iv1"])
    iv2 = bytes.fromhex(sample["iv2"])
    c1 = bytes.fromhex(sample["ct"])[:16]
    p1 = xor(msg[:16], iv1)

    table = {}
    for a in range(1 << bits):
        f = Cipher(algorithms.AES(key(a)), modes.ECB()).encryptor()
        x = f.update(p1) + f.finalize()
        table.setdefault(x, []).append(a)

    for b in range(1 << bits):
        f = Cipher(algorithms.AES(key(b)), modes.ECB()).decryptor()
        x = xor(f.update(c1) + f.finalize(), iv2)
        for a in table.get(x, ()):
            try:
                if dec(sample, a, b) == msg:
                    return a, b
            except ValueError:
                continue

    raise ValueError("no key pair matches the complete calibration message")


def load(path):
    tree = ast.parse(path.read_text())
    data = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                data[node.targets[0].id] = ast.literal_eval(node.value)
    return data


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).resolve().parents[1] / "release" / "output.txt"
    )
    data = load(path)
    start = perf_counter()
    a, b = recover(data["bits"], data["msg"], data["sample"])
    print(dec(data["target"], a, b).decode())
    print(f"Recovered in {perf_counter() - start:.2f}s", file=sys.stderr)
