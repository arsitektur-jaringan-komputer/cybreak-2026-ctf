from hashlib import sha256
from secrets import randbelow
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.number import bytes_to_long
from ecdsa.curves import SECP256k1


flag = b"CYB26{REDACTED}"

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


'''
a = 1862210122919191456937006087619975902871867319544153026310143176945345287102
Q = (86643069776804495499899146886807968526349100437677062437255003160118110335023, 81420961270854479225916175720986974375227915237774382432874118844229706691363)
sigs = [(b'Rudy rolls the Astral Dice.', 3255737783133368661904151236046977886959685060125638095056999554857081446723, 72042923736387675668306577902450976035970430624900172801026565347344789289190), (b'Rudy casts True Randomness.', 115648340686152935035287113356220583806716034342300816081434274492210307668763, 1508090384529371703300702374849476881082033500457188165502753929481723467422), (b'Rudy seals the final prophecy.', 43569892012791923372858707492079630725740279446682364697197032650034928171444, 40961581986523195300069415323655746483585336084594188905952350160730175556662)]
iv = '6d4a80ea5bccf41d082c8a2edcc2492d'
ct = 'fb73fc3e09fcae720e189d763dc2cbaa284e86615468b31611b3e02855d26fe32e3cf9dba8670f976bc21142cdc2a4b3cef8acbf6ea5f03511b389c46c29cfda99060bae6ddb3c3e07235f99d29b49175a5faf8945bcd7014440254ef0cffe3d'
'''
