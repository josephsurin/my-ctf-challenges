# DownUnderCTF 2024 - ESPecially secure boot

- **Category:** pwn
- **Solves:** 3/2194
- **Difficulty:** ⭐️⭐️⭐️
- **Hosting type:** tcp
- **Tags:** ESP32

---

> > The ESP-IDF 2nd stage Bootloader implements functions related to the Secure Boot feature. In previous releases of ESP-IDF releases (2.x, 3.0.5, 3.1), the 2nd stage Bootloader did not sufficiently verify the load address of binary image sections. If the Secure Boot feature was used without the Flash Encryption feature enabled, an attacker could craft a binary which would overwrite parts of the 2nd stage Bootloader’s code whilst the binary file is being loaded. Such a binary could be used to execute arbitrary code, thus bypassing the Secure Boot check.


Handout files:

- [./publish/especially-secure-boot.tar.gz](./publish/especially-secure-boot.tar.gz)

## Solution

Flag: `DUCTF{can_you_exploit_without_the_-seed_arg_set?}`


- [**Solver**](./solve/solv.py)



