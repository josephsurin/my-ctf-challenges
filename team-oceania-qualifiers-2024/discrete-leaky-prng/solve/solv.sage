from binteger import Bin
from tqdm import tqdm
import hashlib, random, _pickle

def dlp_lsb(h):
    return pow(h, (p-1)//2, p) == p - 1

p = 13191541575961523556919722714956371817391121352518410394192489145468852822583880493083532716705308760905081608620870496451228922081367944013348132106497063
g = 5

dat = open('../publish/output.txt', 'r').readlines()
signatures = []
for l in dat[:-1]:
    msg, r, s = l.split()
    signatures.append((int(msg, 16), int(r), int(s)))
enc = int(dat[-1])

mt_bits = []
for i in range(2024):
    for j in range(9):
        mt_bits.append(Bin(signatures[i][0], n=9)[j])
    mt_bits.append(dlp_lsb(signatures[i][1]))
mt_bits = mt_bits[:624*32]

images = _pickle.load(open('./mt-images-precomp.pickle', 'rb'))
M = []
print('building matrix rows...')
for i in tqdm(range(624*32)):
    row = [0] * 624*32
    for k in images[i]:
        row[k] = 1
    row = [row[0]] + row[32:]
    M.append(row)

print('building matrix...')
M = Matrix(GF(2), M)

print('adding outputs to matrix...')
M = M.augment(vector(mt_bits))

print('checking nullity...')
print('nullity is', M.right_nullity())

print('checking solution')
sol = M.right_kernel_matrix()[0][:-1]
sol = [sol[0]] + [0] * 31 + list(sol[1:])
recovered_state = [Bin(sol[i:i+32]).int for i in range(0, 624*32, 32)]
random.setstate((3, tuple(recovered_state + [624]), None))
random.getrandbits(9)
k = random.getrandbits(512)
m, r, s = signatures[0]
h = int(hashlib.sha512(hex(m)[2:].encode()).hexdigest(), 16)
assert r == pow(g, k, p)
x = int((s * k - h) * pow(r, -1, p) % p)
flag = enc ^^ x
print(int(flag).to_bytes(64, 'big').decode())
