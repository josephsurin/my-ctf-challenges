# DownUnderCTF 2024 - kyber decryption oracle

- **Category:** crypto
- **Solves:** 1/2194
- **Difficulty:** ⭐️⭐️⭐️⭐️
- **Hosting type:** tcp
- **Tags:** Kyber

---

> Kyber.CPAPKE is the IND-CPA-secure public key encryption scheme used in the Kyber KEM. Obviously, it is vulnerable to chosen ciphertext attacks. Please prove it by recovering the secret key from this decryption oracle.


Handout files:

- [./publish/build-kyber.sh](./publish/build-kyber.sh)
- [./publish/kyber-decryption-oracle.py](./publish/kyber-decryption-oracle.py)
- [./publish/libpqcrystals_kyber512_ref.so](./publish/libpqcrystals_kyber512_ref.so)

## Solution

Flag: `DUCTF{decryption_oracle_is_too_powerful!!}`


- [**Solver**](./solve/solv.sage)



