from pwn import process
from Crypto.Util.number import bytes_to_long, long_to_bytes
from hashlib import sha256
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

s1, e1 = sign(b'asdf')
s2, e2 = sign(b'zxcv')

s1_ = s1 * pow(2^256 + 1, -1, q) % q
s2_ = s2 * pow(2^256 + 1, -1, q) % q
e1_ = e1 * pow(2^256 + 1, -1, q) % q
e2_ = e2 * pow(2^256 + 1, -1, q) % q

M = Matrix([
    [q,   0,   0,       0],
    [0,   q,   0,       0],
    [e1_, e2_, 2^256/q, 0],
    [s1_, s2_, 0,       2^256]
])
M = M.LLL()

for r in M:
    if r[-1] == 2^256:
        x = int(r[-2] * q / 2^256) % q
        if pow(g, x, p) != y:
            x += 1
        print('Recovered private key:', x)
        break

target_msg = b'right hand'
k = 1337
r = pow(g, k, p) % q
e = bytes_to_long(2 * sha256(long_to_bytes(r) + target_msg).digest()) % q
s = (k - x * e) % q

flag = verify(target_msg, (s, e))
print(flag)
