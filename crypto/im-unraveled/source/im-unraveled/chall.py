#!/usr/bin/env python3

import hashlib
import hmac
from base64 import b32encode
from os import urandom

from Crypto.Cipher import AES

from utils import listener

try:
    FLAG = open("flag.txt").read().strip()
except FileNotFoundError:
    FLAG = "CYB26{local_testing_flag}"

BLOCK = 16
P_LIE = 0.25             
MIN_PAD = 2              
MAX_QUERIES = 25_000     
MAX_CHECK_ATTEMPTS = 3   


def strip_pad(pt):
    n = pt[-1]
    if n < MIN_PAD or n > BLOCK or pt[-n:] != bytes([n]) * n:
        raise ValueError("bad padding")
    return pt[:-n]


class Challenge:
    def __init__(self):

        self.message = b32encode(urandom(10)).decode("ascii")
        self.key = urandom(16)
        self.noise_key = urandom(16)          
        self.query_count = 0
        self.encrypt_count = 0
        self.check_attempts = 0

        self.before_input = "Recover my token and I'll send you the flag.\n"

    def update_query_count(self, n=1):
        self.query_count += n
        if self.query_count >= MAX_QUERIES:
            self.exit = True

    def _lie(self, blob):
        tag = hmac.new(self.noise_key, blob, hashlib.sha256).digest()
        return int.from_bytes(tag[:8], "big") / 2**64 < P_LIE

    def get_ct(self):
        if self.encrypt_count >= 1:
            return {"error": "no more encryptions"}
        self.encrypt_count += 1
        iv = urandom(BLOCK)
        ct = AES.new(self.key, AES.MODE_CBC, iv=iv).encrypt(self.message.encode())
        return {"ct": (iv + ct).hex()}

    def check_padding(self, ct_hex):
        try:
            blob = bytes.fromhex(ct_hex)
        except ValueError:
            return {"error": "ct must be hex"}
        if len(blob) < 2 * BLOCK or len(blob) % BLOCK != 0:
            return {"error": "ct must be an IV followed by >= 1 whole block"}

        iv, body = blob[:BLOCK], blob[BLOCK:]
        pt = AES.new(self.key, AES.MODE_CBC, iv=iv).decrypt(body)
        try:
            strip_pad(pt)
            good = True
        except ValueError:
            good = False

        self.update_query_count()
        return {"result": good ^ self._lie(blob)}

    def check_message(self, message):
        if message == self.message:
            return {"flag": FLAG}
        self.check_attempts += 1
        left = MAX_CHECK_ATTEMPTS - self.check_attempts
        if left <= 0:
            self.exit = True
            return {"error": "incorrect message, no attempts left"}
        return {"error": f"incorrect message, {left} attempt(s) left"}


    def challenge(self, msg):
        if "option" not in msg or msg["option"] not in ("encrypt", "unpad", "check"):
            return {"error": "Option must be one of: encrypt, unpad, check"}

        if msg["option"] == "encrypt":
            return self.get_ct()
        if msg["option"] == "unpad":
            return self.check_padding(msg["ct"])
        if msg["option"] == "check":
            return self.check_message(msg["message"])


import builtins; builtins.Challenge = Challenge
listener.start_server(port=13337)
