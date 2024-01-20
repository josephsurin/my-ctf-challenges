import os, random, hashlib
from string import ascii_letters


FLAG = os.getenv('FLAG', 'oiccflag{??????????????????????????????????????????????????????}').encode()
assert len(FLAG) == 64


def randstr(n):
    return ''.join(random.choice(ascii_letters) for _ in range(n))


def q1_warmup():
    s = randstr(8)
    c = ''.join(ascii_letters[(ascii_letters.index(x) + 13) % len(ascii_letters)] for x in s)
    return s, c


def q2_rsa():
    s = randstr(12)
    n = 232541361594175578632027127993608966831
    e = 17
    m = int.from_bytes(s.encode(), 'big')
    c = pow(m, e, n)
    return s, (n ,e, c)


def q3_rsa():
    s = randstr(17)
    n = 207807003139618432986747701281335329267
    e = 17
    m = int.from_bytes(s.encode(), 'big')
    c = pow(m, e, n)
    return s, (n, e, c)


def q4_dlp():
    s = randstr(9)
    p = 39288428804729492910744245254228480207191648963558423426647630852176554102366931740577474243244577534999086349567983
    g = 31
    x = int.from_bytes(s.encode(), 'big')
    c = pow(g, x, p)
    return s, (g, p, c)


def q5_dlp():
    s = randstr(15)
    p = 29517605817158342537249085665907349858422623576577415357604310223149476409345714471227558569629224037210132313355207
    g = 31
    x = int.from_bytes(s.encode(), 'big')
    c = [pow(g, x ^ (1 << i), p) for i in range(x.bit_length())]
    return s, (g, p, c)


def q6_ecc():
    p = 105255139442591765914580197916433817179838481965344976343857730042442182855807
    a = 3
    b = 7
    while True:
        s = randstr(32)
        Gx = int.from_bytes(s.encode(), 'big')
        Gy2 = Gx**3 + a*Gx + b
        if pow(Gy2, (p-1)//2, p) == 1:
            Gy = pow(Gy2, (p+1)//4, p)
            break
    m = (3 * Gx**2 + a) * pow(2 * Gy, -1, p) % p
    Px = (m**2 - 2 * Gx) % p
    Py = (m * (Gx - Px) - Gy) % p
    return s, (p, a, b, Py)


questions = [q1_warmup, q2_rsa, q3_rsa, q4_dlp, q5_dlp, q6_ecc]
answers = ''
for i, q in enumerate(questions):
    ans, given = q()
    answers += ans
    print(f'question {i+1}:', given)
print('self checker:', hashlib.md5(answers.encode()).hexdigest())
key = hashlib.sha512(answers.encode()).digest()
flag_enc = bytes([f ^ k for f, k in zip(FLAG, key)])
print('flag enc:', flag_enc.hex())
