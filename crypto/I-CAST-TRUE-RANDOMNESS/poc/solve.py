#!/usr/bin/env python3

import ast
import sys
from hashlib import sha256
from pathlib import Path
from random import Random
from time import perf_counter

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

N = 19937


class MT:

    def __init__(self):
        self.s = [[0] * 31 + [1]]
        self.s += [[1 << (1 + 32 * i + j) for j in range(32)] for i in range(623)]
        self.i = 624

    def twist(self):
        s = self.s
        for i in range(624):
            y = s[(i + 1) % 624][:31] + [s[i][31]]
            z = s[(i + 397) % 624]
            s[i] = [z[j] ^ (y[j + 1] if j < 31 else 0)
                    ^ (y[0] if (0x9908B0DF >> j) & 1 else 0)
                    for j in range(32)]
        self.i = 0

    def next(self):
        if self.i == 624:
            self.twist()
        y = self.s[self.i][:]
        self.i += 1
        y = [y[j] ^ (y[j + 11] if j < 21 else 0) for j in range(32)]
        y = [y[j] ^ (y[j - 7] if j >= 7 and (0x9D2C5680 >> j) & 1 else 0)
             for j in range(32)]
        y = [y[j] ^ (y[j - 15] if j >= 15 and (0xEFC60000 >> j) & 1 else 0)
             for j in range(32)]
        return [y[j] ^ (y[j + 18] if j < 14 else 0) for j in range(32)]


class GF2:
    def __init__(self, n=N):
        self.rows = [0] * n
        self.rhs = [0] * n
        self.rank = 0

    def add(self, row, bit):
        while row:
            p = row.bit_length() - 1
            if self.rows[p]:
                row ^= self.rows[p]
                bit ^= self.rhs[p]
            else:
                self.rows[p], self.rhs[p] = row, bit
                self.rank += 1
                return
        if bit:
            raise ValueError("inconsistent equations: check the log and MT model")

    def solve(self):
        if self.rank != len(self.rows):
            raise ValueError(f"insufficient rank: {self.rank}/{len(self.rows)}")
        x = 0
        
        for p, row in enumerate(self.rows):
            if self.rhs[p] ^ ((row & x).bit_count() & 1):
                x |= 1 << p
        return x


def roll(r, i):
    a, b = r.getrandbits(32), r.getrandbits(32)
    b = ((b << 7) | (b >> 25)) & 0xFFFFFFFF
    if (i + 1) % 8 == 0:
        r.getrandbits(32)
    return (a ^ b) >> 16


def key(r):
    x = b"".join(r.getrandbits(32).to_bytes(4, "big") for _ in range(8))
    return sha256(x).digest()


def restore(x):
    s = [((x & 1) << 31)]
    s += [(x >> (1 + 32 * i)) & 0xFFFFFFFF for i in range(623)]
    r = Random(0)
    r.setstate((3, tuple(s) + (624,), None))
    return r


def replay(r, leak):
    for i, v in enumerate(leak):
        if roll(r, i) != v:
            raise ValueError(f"prediction disagrees with observation {i}")
    return r


def recover(leak):
    if not isinstance(leak, list) or len(leak) * 16 < N:
        raise ValueError("not enough observations to recover the full state")
    if any(type(v) is not int or not 0 <= v < 2**16 for v in leak):
        raise ValueError("observations must be unsigned 16-bit integers")

    m, g = MT(), GF2()
    used = 0
    for i, v in enumerate(leak):
        a, b = m.next(), m.next()
        if (i + 1) % 8 == 0:
            m.next()
        for j in range(16, 32):
            row = a[j] ^ b[(j - 7) % 32]
            g.add(row, (v >> (j - 16)) & 1)
        used = i + 1
        if g.rank == N:
            break

    x = g.solve()
    r = replay(restore(x), leak)
    return r, used, g.rank


def read_data(text):
    tree = ast.parse(text)
    data = {}

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                data[node.targets[0].id] = ast.literal_eval(node.value)

    if set(data) != {"leak", "iv", "ct", "N"}:
        raise ValueError("expected leak, iv, ct and N in output.txt")

    if data["N"] != N:
        raise ValueError("unexpected MT state size")

    return data


def load(path):
    return read_data(path.read_text())


def decrypt(data, r):
    return AESGCM(key(r)).decrypt(bytes.fromhex(data["iv"]),
                                  bytes.fromhex(data["ct"]), None)


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).resolve().parents[1] / "release" / "output.txt"
    )
    data = load(path)
    start = perf_counter()
    r, used, rank = recover(data["leak"])
    flag = decrypt(data, r)
    print(flag.decode())
    print(f"Rank {rank}/{N}; solved with {used} observations; "
          f"verified {len(data['leak'])}; {perf_counter() - start:.2f}s",
          file=sys.stderr)
