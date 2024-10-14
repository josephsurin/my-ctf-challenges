from sage.all import *
import ctypes
import hashlib

kyber_lib = ctypes.CDLL('../publish/libpqcrystals_kyber1024_ref.so')
q = 3329
k = 4
F = GF(q)
P = PolynomialRing(F, 'X')
P.inject_variables()
R = P.quotient_ring(X**256 + 1, 'Xbar')

def hash_h(m):
    return hashlib.sha3_256(m).digest()

def hash_g(m):
    return hashlib.sha3_512(m).digest()

def kdf(m):
    return hashlib.shake_256(m).digest(32)

def bytes_to_polyvec(b):
    polyvec = (ctypes.c_int16 * int(k * 256))()
    kyber_lib.pqcrystals_kyber1024_ref_polyvec_frombytes(polyvec, ctypes.c_buffer(b))
    return vector(R, [R(list(polyvec)[:256]), R(list(polyvec)[256:512]), R(list(polyvec)[512:768]), R(list(polyvec)[768:1024])])

def compressed_bytes_to_poly(b):
    poly = (ctypes.c_int16 * int(256))()
    kyber_lib.pqcrystals_kyber1024_ref_poly_decompress(poly, ctypes.c_buffer(b))
    return R(list(poly))

def poly_frommsg(m):
    poly = (ctypes.c_int16 * int(256))()
    kyber_lib.pqcrystals_kyber1024_ref_poly_frommsg(poly, ctypes.c_buffer(m))
    return R(list(poly))

def poly_tomsg(p):
    poly = (ctypes.c_int16 * int(256))(*list(p))
    buf = ctypes.c_buffer(32)
    kyber_lib.pqcrystals_kyber1024_ref_poly_tomsg(buf, poly)
    return bytes(buf)

def unpack_pk(pk_bytes):
    buf = pk_bytes[:k * 384]
    pv = bytes_to_polyvec(buf)
    seed = pk_bytes[k * 384:]
    return pv, seed

def unpack_sk(sk_bytes):
    return bytes_to_polyvec(sk_bytes)

def unpack_ciphertext(ct_bytes):
  b = bytes_to_polyvec(ct_bytes[:k*384])
  v = compressed_bytes_to_poly(ct_bytes[k*384:k*384+160])
  return (b, v)

def gen_matrix(seed, transposed=0):
    out = ((ctypes.c_int16 * int(k * 256)) * int(k))()
    kyber_lib.pqcrystals_kyber1024_ref_gen_matrix(out, ctypes.c_buffer(seed), transposed)
    return Matrix(R, [vector(R, [R(list(out)[i][j*256:(j+1)*256])for j in range(4)]) for i in range(k)])

def poly_invntt(p):
    t = (ctypes.c_int16 * int(256))(*list(p))
    kyber_lib.pqcrystals_kyber1024_ref_invntt(t)
    t = R(list(t)) / 2**16
    return t

def polyvec_invntt(pv):
    return vector(R, [poly_invntt(p) for p in pv])
