from pwn import process
from Crypto.Util.number import bytes_to_long, long_to_bytes
from hashlib import md5
import ast

def sign(msg):
    conn.sendlineafter(b'> ', b'S')
    conn.sendlineafter(b'message> ', msg.hex().encode())
    return ast.literal_eval(conn.recvline().decode().strip().split('Signature: ')[1])

def verify(msg, sig):
    conn.sendlineafter(b'> ', b'V')
    conn.sendlineafter(b'message> ', msg.hex().encode())
    conn.sendlineafter(b's> ', str(sig[0]).encode())
    conn.sendlineafter(b'e> ', str(sig[1]).encode())
    return conn.recvline().decode().strip()

conn = process('./chall.py')

g = int(conn.recvline().decode().strip().split('g: ')[1])
y = int(conn.recvline().decode().strip().split('y: ')[1])
p = int(conn.recvline().decode().strip().split('p: ')[1])
q = (p - 1) // 2

# collision from https://en.wikipedia.org/wiki/MD5#Collision_vulnerabilities
m1 = bytes.fromhex('d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f8955ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5bd8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70')
m2 = bytes.fromhex('d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f8955ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5bd8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70')

s1, e1 = sign(m1)
s2, e2 = sign(m2)
x = (s1 - s2) * pow(e2 - e1, -1, q) % q
print('Recovered private key:', x)

target_msg = b'I am the left hand'
k = 1337
r = pow(g, k, p) % q
e = bytes_to_long(md5(long_to_bytes(r) + target_msg).digest()) % q
s = (k - x * e) % q

flag = verify(target_msg, (s, e))
print(flag)
