#!/usr/bin/env python3

from hashlib import sha256
from os import urandom
from pathlib import Path
from pprint import pformat
from random import Random

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

N = 2400


def roll(r, i):
    a = r.getrandbits(32)
    b = r.getrandbits(32)
    b = ((b << 7) | (b >> 25)) & 0xFFFFFFFF
    if (i + 1) % 8 == 0:
        r.getrandbits(32)
    return (a ^ b) >> 16


def key(r):
    x = b"".join(r.getrandbits(32).to_bytes(4, "big") for _ in range(8))
    return sha256(x).digest()


def make(flag):
    r = Random(urandom(32))
    leak = [roll(r, i) for i in range(N)]
    k = key(r)
    iv = urandom(12)
    ct = AESGCM(k).encrypt(iv, flag, None)
    return leak, iv.hex(), ct.hex()


if __name__ == "__main__":
    flag = Path(__file__).with_name("flag.txt").read_bytes().rstrip(b"\r\n")
    leak, iv, ct = make(flag)
    print("leak =", pformat(leak, width=96, compact=True))
    print("iv =", repr(iv))
    print("ct =", repr(ct))
    print("N =", 19937)
