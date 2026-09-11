#!/usr/bin/env python3

from base64 import b32encode
from os import urandom

from Crypto.Cipher import AES

from utils import listener, noise

FLAG = "CYB26{REDACTED}"

BLOCK = 16
MIN_PAD = 2
MAX_QUERIES = 50_000
FLAG_BUDGET = 10_000
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
        self.session_key = urandom(16)
        self.query_count = 0
        self.encrypt_count = 0
        self.check_attempts = 0

        self.before_input = (
            "Recover my token and I'll send you the flag.\n"
            "The token is 16 base32 characters (A-Z, 2-7).\n"
            'options: {"option": "encrypt"} -> {"ct": "<hex IV||C0>"}, once per connection\n'
            '         {"option": "unpad", "ct": "<hex>"} -> {"result": <bool>}\n'
            '         {"option": "check", "message": "<token>"} -> {"flag": "..."}\n'
            f"budget: {FLAG_BUDGET} unpad queries for the flag, {MAX_QUERIES} hard cap, "
            f"{MAX_CHECK_ATTEMPTS} check attempts\n"
        )

    def update_query_count(self, n=1):
        self.query_count += n
        if self.query_count >= MAX_QUERIES:
            self.exit = True

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
        return {"result": noise.distort(self.session_key, blob, good)}

    def check_message(self, message):
        if message == self.message:
            if self.query_count <= FLAG_BUDGET:
                return {"flag": FLAG}
            over = self.query_count / FLAG_BUDGET
            self.exit = True
            return {"error": f"token correct, but you spent {self.query_count} queries "
                             f"({over:.1f}x the {FLAG_BUDGET} budget). The flag needs "
                             f"{FLAG_BUDGET} or fewer. Reconnect for a fresh token."}
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
