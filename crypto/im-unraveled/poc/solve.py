#!/usr/bin/env python3

import json
import math
import os
import string
import sys

from pwn import remote

HOST = os.environ.get("CHALL_HOST", "cybreak.miraii.dev")
PORT = int(os.environ.get("CHALL_PORT", "13337"))

BLOCK = 16
ALPHABET = (string.ascii_uppercase + "234567").encode()
P_LIE = 0.25
P_HI, P_LO = 1.0 - P_LIE, P_LIE

STEP_VALID = math.log(P_HI / P_LO)
STEP_BAD = math.log((1 - P_HI) / (1 - P_LO))
UPPER = math.log((1 - 1e-6) / 1e-6)
LOWER = math.log(1e-5 / (1 - 1e-5))            
LOWER_PAIR = math.log(1e-3 / (1 - 1e-3))       

queries = 0


def connect():
    io = remote(HOST, PORT)
    io.recvline()
    return io


def encrypt(io):
    io.sendline(b'{"option": "encrypt"}')
    return bytes.fromhex(json.loads(io.recvline())["ct"])


def oracle(io, blob):
    global queries
    io.sendline(json.dumps({"option": "unpad", "ct": blob.hex()}).encode())
    resp = json.loads(io.recvline())
    if "result" not in resp:
        raise RuntimeError(f"oracle stopped: {resp} (after {queries} queries)")
    queries += 1
    return bool(resp["result"])


def query_pad(io, prev, target, forced):
    L = BLOCK - min(forced)
    tamper = bytearray(os.urandom(BLOCK))
    for pos, pb in forced.items():
        tamper[pos] = pb ^ prev[pos] ^ L
    return oracle(io, os.urandom(BLOCK) + bytes(tamper) + target)


def recover_pair(io, prev, target):
    pairs = [(a, b) for a in ALPHABET for b in ALPHABET]
    llr = {p: 0.0 for p in pairs}
    alive = list(pairs)
    while len(alive) > 1:
        for p in list(alive):
            if p not in llr:
                continue
            a, b = p
            r = query_pad(io, prev, target, {14: a, 15: b})
            llr[p] += STEP_VALID if r else STEP_BAD
            if llr[p] >= UPPER:
                return p
            if llr[p] <= LOWER_PAIR:
                alive.remove(p)
                del llr[p]
    return alive[0]


def recover_byte(io, prev, target, j, known):
    L = BLOCK - j
    llr = {c: 0.0 for c in ALPHABET}
    alive = list(ALPHABET)
    winner, k = None, 0
    while winner is None and len(alive) > 1:
        c = alive[k % len(alive)]
        k += 1
        forced = {j: c}
        for t, pb in enumerate(known):
            forced[j + 1 + t] = pb
        r = query_pad(io, prev, target, forced)
        llr[c] += STEP_VALID if r else STEP_BAD
        if llr[c] >= UPPER:
            winner = c
        elif llr[c] <= LOWER:
            alive.remove(c)
            del llr[c]
            k = 0
    best = winner or (alive[0] if len(alive) == 1 else max(llr, key=llr.get))
    others = [v for cc, v in llr.items() if cc != best]
    return best, llr.get(best, 0.0) - (max(others) if others else 0.0)


def recover_block(io, prev, target):
    plain = bytearray(BLOCK)
    plain[14], plain[15] = recover_pair(io, prev, target)
    print(f"  bytes 14,15 = {chr(plain[14])!r}{chr(plain[15])!r}   ({queries} q)", file=sys.stderr)
    margins = {}
    for j in range(13, -1, -1):
        plain[j], margins[j] = recover_byte(io, prev, target, j, plain[j + 1:])
        print(f"  byte {j:2d} = {chr(plain[j])!r}   ({queries} q)", file=sys.stderr)
    return plain, margins


def check(io, token):
    io.sendline(json.dumps({"option": "check", "message": token}).encode())
    return json.loads(io.recvline())


def main():
    io = connect()
    blob = encrypt(io)          
    iv, c0 = blob[:16], blob[16:32]

    plain, margins = recover_block(io, iv, c0)
    token = bytes(plain).decode("ascii", "replace")
    print(f"[+] {token}   ({queries} queries)", file=sys.stderr)
    resp = check(io, token)
    if "flag" in resp:
        print(resp["flag"])
        return

    for j in sorted(sorted(margins, key=margins.get)[:3], reverse=True):
        plain[j], _ = recover_byte(io, iv, c0, j, plain[j + 1:])
    resp = check(io, bytes(plain).decode("ascii", "replace"))
    print(resp.get("flag") or "[-] gave up")


if __name__ == "__main__":
    main()
