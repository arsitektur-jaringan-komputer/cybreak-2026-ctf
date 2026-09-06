from hashlib import sha256
from secrets import randbelow
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.number import bytes_to_long
from ecdsa.curves import SECP256k1


flag = open("flag.txt", "rb").read().strip()

G = SECP256k1.generator
n = SECP256k1.order

d = randbelow(n - 1) + 1
Q = d * G

a = randbelow(n - 2) + 2
b = randbelow(n - 1) + 1
k = randbelow(n - 1) + 1

msgs = [
    b"Rudy rolls the Astral Dice.",
    b"Rudy casts True Randomness.",
    b"Rudy seals the final prophecy.",
]

sigs = []

for msg in msgs:
    k = (a * k + b) % n
    assert k != 0

    z = bytes_to_long(sha256(msg).digest())
    R = k * G
    r = int(R.x()) % n
    s = (z + r * d) * pow(k, -1, n) % n
    sigs.append((msg, r, s))

key = sha256(d.to_bytes(32, "big")).digest()
iv = get_random_bytes(16)
ct = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(flag, 16))

print("a =", a)
print("Q =", (int(Q.x()), int(Q.y())))
print("sigs =", sigs)
print("iv =", repr(iv.hex()))
print("ct =", repr(ct.hex()))
