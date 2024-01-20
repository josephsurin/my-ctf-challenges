import itertools
from tqdm import tqdm

p = 4551037765311920851
P = [int(x) for x in open('../publish/output.txt', 'r').readlines()]

F = GF(p)
R.<x0, x1, x2, x3, x4> = PolynomialRing(F)
for K in tqdm(list(itertools.product(range(2**4), repeat=5))):
    K = [-k for k in K]
    a4 = -(P[0] + K[0])
    a3 = (P[1] + K[1] + a4 * (P[0] + K[0])) * pow(-2, -1, p)
    a2 = (P[2] + K[2] + a4 * (P[1] + K[1]) + a3 * (P[0] + K[0])) * pow(-3, -1, p)
    a1 = (P[3] + K[3] + a4 * (P[2] + K[2]) + a3 * (P[1] + K[1]) + a2 * (P[0] + K[0])) * pow(-4, -1, p)
    a0 = (P[4] + K[4] + a4 * (P[3] + K[3]) + a3 * (P[2] + K[2]) + a2 * (P[1] + K[1]) + a1 * (P[0] + K[0])) * pow(-5, -1, p)

    R.<x> = PolynomialRing(F)
    f = a0 + a1 * x + a2 * x^2 + a3 * x^3 + a4 * x^4 + x^5
    roots = f.roots()

    flag_parts = []
    for v_, _ in roots:
        for v in v_.nth_root(7, all=True):
            m = int(v).to_bytes(8, 'big')
            if not m.isascii():
                m = int((int(v) + p)).to_bytes(8, 'big')
            try:
                flag_parts.append(m.decode())
            except:
                continue
    if len(flag_parts) == 5:
        print(K)
        print('\n'.join(flag_parts))
        break
