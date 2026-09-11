#!/usr/bin/env python3

import json
import os
import string
import sys

from pwn import remote

HOST = os.environ.get("CHALL_HOST", "cybreak.miraii.dev")
PORT = int(os.environ.get("CHALL_PORT", "13337"))

BLOCK = 16
ALPHABET = (string.ascii_uppercase + "234567").encode()

T_PAIR = 16
T_BYTE = 12

queries = 0


def connect():
    io = remote(HOST, PORT)
    io.recvuntil(b"check attempts\n")
    return io


def calibrate(n=500):
    io = connect()
    trues = 0
    for _ in range(n):
        io.sendline(json.dumps({"option": "unpad", "ct": os.urandom(48).hex()}).encode())
        trues += bool(json.loads(io.recvline())["result"])
    io.close()
    return trues / n


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


def ask(io, prev, target, guess):
    L = BLOCK - min(guess)
    tamper = bytearray(os.urandom(BLOCK))
    for pos, byte in guess.items():
        tamper[pos] = byte ^ prev[pos] ^ L
    return oracle(io, os.urandom(BLOCK) + bytes(tamper) + target)


def recover_pair(io, prev, target):
    pairs = [(a, b) for a in ALPHABET for b in ALPHABET]
    score = [0] * len(pairs)
    lead = 0
    while score[lead] < T_PAIR:
        a, b = pairs[lead]
        score[lead] += 1 if ask(io, prev, target, {14: a, 15: b}) else -1
        lead = score.index(max(score))
    return pairs[lead]


def recover_byte(io, prev, target, j, tail):
    score = [0] * len(ALPHABET)
    lead = 0
    while score[lead] < T_BYTE:
        guess = {j: ALPHABET[lead]}
        for offset, byte in enumerate(tail):        
            guess[j + 1 + offset] = byte
        score[lead] += 1 if ask(io, prev, target, guess) else -1
        lead = score.index(max(score))
    return ALPHABET[lead]


def main():
    print(f"[*] measured lie rate: {calibrate():.3f}", file=sys.stderr)

    io = connect()
    blob = encrypt(io)                              
    iv, c0 = blob[:16], blob[16:32]

    token = bytearray(BLOCK)
    token[14], token[15] = recover_pair(io, iv, c0)
    boot = queries
    print(f"  14,15 = {chr(token[14])}{chr(token[15])}   ({boot} q)", file=sys.stderr)

    for j in range(13, -1, -1):
        token[j] = recover_byte(io, iv, c0, j, token[j + 1:])
        print(f"  byte {j:2d} = {chr(token[j])}   ({queries} q)", file=sys.stderr)

    guess = bytes(token).decode("ascii", "replace")
    print(f"[+] {guess}   ({queries} queries, {boot} on the pair)", file=sys.stderr)

    io.sendline(json.dumps({"option": "check", "message": guess}).encode())
    resp = json.loads(io.recvline())
    print(resp.get("flag") or resp.get("error"))


if __name__ == "__main__":
    main()
