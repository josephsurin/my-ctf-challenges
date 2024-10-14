from Crypto.Cipher import AES

import kyber1024_util as kyber_util

"""
Let v_i be the elements returned by each call to poly_getnoise_eta2 within the
encapsulation procedure. Because the nonce is decremented, some of the random
error term values are the same. We have:

r = (v0, v1, v2, v3)
e1 = (v3, v2, v1, v0)
e2 = v0

u = Ar + e1
v = t*r + e2 + m

u = (
    A00 v0 + A01 v1 + A02 v2 + A03 v3 + v3,
    A10 v0 + A11 v1 + A12 v2 + A13 v3 + v2,
    A20 v0 + A21 v1 + A22 v2 + A23 v3 + v1,
    A30 v0 + A31 v1 + A32 v2 + A33 v3 + v0,
) = (
    A00 v0 + A01 v1 + A02 v2 + (A03 + 1) v3,
    A10 v0 + A11 v1 + (A12 + 1) v2 + A13 v3,
    A20 v0 + (A21 + 1) v1 + A22 v2 + A23 v3,
    (A30 + 1) v0 + A31 v1 + A32 v2 + A33 v3,
)
v = t0 v0 + t1 v1 + t2 v2 + t3 v3 + v0 + m

(v0, v1, v2, v3) can be recovered from u by solving a system of equations.
These then allow for recovery of m.
Then we can follow the procedure to compute the shared secret from the
decrypted randomness and use it to decrypt the flag.
"""

data = open('../publish/output.txt', 'r').read().splitlines()
kyber_pk = bytes.fromhex(data[0].split(': ')[1])
kyber_ct = bytes.fromhex(data[1].split(': ')[1])
flag_ct = bytes.fromhex(data[2].split(': ')[1])

t, A_seed = kyber_util.unpack_pk(kyber_pk)
A = kyber_util.gen_matrix(A_seed)
t = kyber_util.polyvec_invntt(t)
A = Matrix(kyber_util.R, [kyber_util.polyvec_invntt(a) for a in A])

c1, c2 = kyber_util.unpack_ciphertext(kyber_ct)

A_plus_e1 = Matrix(A).T
A_plus_e1 += Matrix([
    [0, 0, 0, 1],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [1, 0, 0, 0],
])
r = ~A_plus_e1 * c1
m = c2 - t * r - r[0]
msg = kyber_util.poly_tomsg(m)
kr = kyber_util.hash_g(msg + kyber_util.hash_h(kyber_pk))
ss = kr[:32]

flag = AES.new(bytes(ss), AES.MODE_CTR, nonce=b'x'*12).decrypt(flag_ct)
print(flag.decode())
