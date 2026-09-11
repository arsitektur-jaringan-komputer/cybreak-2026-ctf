#!/usr/bin/env python3
"""Server-side only. This file is deliberately not part of the handout."""

import hashlib
import hmac

P_LIE = 0.25


def distort(key, blob, verdict):
    tag = hmac.new(key, blob, hashlib.sha256).digest()
    flip = int.from_bytes(tag[:8], "big") / 2**64 < P_LIE
    return verdict ^ flip
