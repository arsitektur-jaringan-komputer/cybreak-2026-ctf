

from math import gcd
from Crypto.Util.number import bytes_to_long, getPrime


flag = b"CYB26{rudy_said_:ohh_come_on_event_with_nat_20_still_not_working!!!_i_must_go_back_to_the_academy}"

e1 = 17
e2 = 65537

while True:
    p = getPrime(512)
    q = getPrime(512)
    phi = (p - 1) * (q - 1)

    if p != q and gcd(e1, phi) == gcd(e2, phi) == 1:
        break

n = p * q
m = bytes_to_long(flag)

assert m < n and gcd(m, n) == 1

c1 = pow(m, e1, n)
c2 = pow(m, e2, n)

print("n =", n)
print("e1 =", e1)
print("e2 =", e2)
print("c1 =", c1)
print("c2 =", c2)
