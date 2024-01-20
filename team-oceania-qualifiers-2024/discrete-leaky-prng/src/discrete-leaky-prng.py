import os
import random
import hashlib

FLAG = os.getenv('FLAG', 'oiccflag{??????????????????????????????????????????????????????}').encode()
assert len(FLAG) == 64

P_BITS = 512
p = 13191541575961523556919722714956371817391121352518410394192489145468852822583880493083532716705308760905081608620870496451228922081367944013348132106497063
assert p.bit_length() == P_BITS

def dsa_sign(msg, x):
    h = int(hashlib.sha512(msg).hexdigest(), 16)
    k = random.getrandbits(P_BITS)
    r = pow(g, k, p)
    s = pow(k, -1, p) * (h + x * r) % p
    return (r, s)

g = 5
x = random.getrandbits(P_BITS)
y = pow(g, x, p)

signatures = []
for i in range(2024):
    msg = hex(random.getrandbits(9))[2:]
    r, s = dsa_sign(msg.encode(), x)
    print(msg, r, s)

print(int.from_bytes(FLAG, 'big') ^ x)
