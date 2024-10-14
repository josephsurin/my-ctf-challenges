import os
from ctypes import CDLL, c_buffer
from Crypto.Cipher import AES

FLAG = os.getenv('FLAG', 'bwctf{testflag}').encode()

kyber_lib = CDLL('./libpqcrystals_kyber1024_ref.so')
class Kyber:
    def __init__(self):
        self.pk_buf = c_buffer(1568)
        self.sk_buf = c_buffer(3168)
        kyber_lib.pqcrystals_kyber1024_ref_keypair(self.pk_buf, self.sk_buf)

    def kem_enc(self):
        ct_buf = c_buffer(1696)
        ss_buf = c_buffer(32)
        kyber_lib.pqcrystals_kyber1024_ref_enc(ct_buf, ss_buf, self.pk_buf)
        return bytes(ct_buf), bytes(ss_buf)

kyber = Kyber()
kyber_ct, ss = kyber.kem_enc()

flag_ct = AES.new(ss, AES.MODE_CTR, nonce=b'x'*12).encrypt(FLAG)

print('kyber_pk:', bytes(kyber.pk_buf).hex())
print('kyber_ct:', kyber_ct.hex())
print('flag_ct:', flag_ct.hex())
