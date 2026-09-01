from math import gcd
from Crypto.Hash import SHA256
from Crypto.Util.number import bytes_to_long, getPrime, inverse

e = 65537

def genkeys(bits=512):
    while True:
        p = getPrime(bits)
        q = getPrime(bits)
        phi = (p-1)*(q-1)
        if p != q and gcd(e, phi) == 1:
            return p, q, p*q, inverse(e, phi)

def encrypt(msg, n):
    m = bytes_to_long(msg)
    assert m < n
    return pow(m, e, n)

def crt_sign(msg, p, q, d):
    h = bytes_to_long(SHA256.new(msg).digest())
    sp = pow(h, d % (p-1), p)
    sq = pow(h, d % (q-1), q)

    def combine(sp):
        h_ = (sp - sq) * inverse(q, p) % p
        return sq + q * h_

    good = combine(sp)
    bad = combine((sp + 1) % p) 
    return good, bad

p, q, n, d = genkeys()
msg = b"CYB26{remember_to_use_luck_magic_to_boost_your_roll_before_casting_guyssssss_if_its_still_bad_just_burn_the_scroll}"

s1, s2 = crt_sign(msg, p, q, d)
c = encrypt(msg, n)

print("n =", n)
print("e =", e)
print("valid_signature =", s1)
print("faulty_signature =", s2)
print("c =", c)

