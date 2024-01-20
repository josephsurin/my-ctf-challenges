from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

"""
ECB cut and paste puzzle! Obtain C1, C2 and C3 from the oracle, then construct
the final payload C1 || C1 || C2 || C3. This exploits the Python behaviour
where strings separated by whitespace are concatenated, and also that curly
braces are not filtered so f-strings can be used to leak variables.

print("          f")[  PADDING ]
|---------------|---------------
       C1               C2

print("         {KEY}")[PADDING]
|---------------|---------------
       C1               C3


print("         print("          f")[  PADDING ]{KEY}")[PADDING]
|---------------|---------------|---------------|---------------
       C1               C1             C2              C3

After obtaining the key, any command can be encrypted, such as print(FLAG) or
os.system('/bin/bash').
"""

def enc_oracle(payload):
    conn.sendlineafter(b'> ', b'1')
    conn.sendlineafter(b'Enter your words to say: ', payload.encode())
    ct1 = bytes.fromhex(conn.recvline().decode().split('Encrypted echo command: ')[1])
    c1, c2 = ct1[:16], ct1[16:]
    return c1, c2

def use_cmd(payload):
    conn.sendlineafter(b'> ', b'2')
    conn.sendlineafter(b'Enter your encrypted command: ', payload.hex().encode())

# conn = process(['python3', '../src/server.py'])
conn = remote('0.0.0.0', 1337)

payload1 = '          f'
C1, C2 = enc_oracle(payload1)

payload2 = '         {KEY}'
_, C3 = enc_oracle(payload2)

payload = C1 + C1 + C2 + C3
use_cmd(payload)
o = conn.recvline()
key = o.split(b'\x0c' * 0xc)[1][:-1][2:-1].decode('unicode_escape').encode('latin-1')
cmd = AES.new(key, AES.MODE_ECB).encrypt(pad(b'print(FLAG)', 16))
use_cmd(cmd)
print(conn.recvline().decode())
conn.close()
