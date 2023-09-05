# DownUnderCTF 2023 - shifty mem

- **Category:** pwn
- **Solves:** 40/2073
- **Difficulty:** ⭐️⭐️
- **Hosting type:** tcp
- **Tags:** Race condition, Buffer overflow

---

> Shifting as a SUID binary service, because why not?
> 
> Note: This challenge runs over TLS on port 443. You can connect with `openssl` (`openssl s_client -quiet -connect <hostname>:443`) or `pwntools` (`remote('<hostname>', 443, ssl=True)`). This shouldn't affect exploitation.
> 
> 
> Estimated startup time: 30 seconds


Handout files:

- [./publish/shifty_mem.c](./publish/shifty_mem.c)
- [./publish/shifty_mem](./publish/shifty_mem)

## Solution

Flag: `DUCTF{r4c1ng_sh4r3d_m3mory_t0_th3_f1nish_flag}`


- [**Solver**](./solve/exploit.c)



