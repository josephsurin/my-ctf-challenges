import ast, hashlib
from string import ascii_letters


def solve_q1(given):
    c = given
    s = ''.join(ascii_letters[(ascii_letters.index(x) - 13) % len(ascii_letters)] for x in c)
    return s


def solve_q2(given):
    n, e, c = given
    roots = Mod(c, n).nth_root(e, all=True)
    for r in roots:
        if r < 256^12:
            s = int(r).to_bytes(12, 'big')
            return s.decode()


def solve_q3(given):
    n, e, c = given
    m = int(Mod(c, n).nth_root(e))
    while True:
        m += n
        s = int(m).to_bytes(17, 'big')
        if s.isalpha():
            return s.decode()


def solve_q4(given):
    g, p, c = given
    f1 = 12423799711
    f2 = 313044081347
    assert (p - 1) % f1 == (p - 1) % f2 == 0
    F = GF(p)
    x1 = discrete_log(F(c)^((p-1)//f1), F(g)^((p-1)//f1), ord=f1)
    x2 = discrete_log(F(c)^((p-1)//f2), F(g)^((p-1)//f2), ord=f2)
    x = crt([x1, x2], [f1, f2])
    s = int(x).to_bytes(9, 'big')
    return s.decode()


def solve_q5(given):
    g, p, c = given
    x = 0
    g_x = (c[0] * pow(g, -1, p)) % p
    # g_x = (c[0] * g) % p # depending on the LSB of x
    for i, c_ in enumerate(c):
        if c_ != g_x * pow(g, 1 << i, p) % p:
            x |= 1 << i
    s = int(x).to_bytes(15, 'big')
    return s.decode()


def solve_q6(given):
    p, a, b, Py = given
    E = EllipticCurve(GF(p), [a, b])
    P.<x> = GF(p)[]
    roots = (x^3 + a*x + b - Py^2).roots()
    for Px, _ in roots:
        P = E.lift_x(Px)
        for G in P.division_points(2):
            s = int(G.xy()[0]).to_bytes(32, 'big')
            if s.isascii():
                return s.decode()


dat = open('../publish/output.txt', 'r').readlines()
checker = dat[-2].split('self checker: ')[1].strip()
flag_enc = bytes.fromhex(dat[-1].split('flag enc: ')[1])
givens = []
for i in range(6):
    given = dat[i].split(f'question {i+1}: ')[1].strip()
    if given[0] == '(':
        given = ast.literal_eval(given)
    givens.append(given)
solvers = [solve_q1, solve_q2, solve_q3, solve_q4, solve_q5, solve_q6]
answers = ''
for i in range(6):
    ans = solvers[i](givens[i])
    answers += ans
if hashlib.md5(answers.encode()).hexdigest() == checker:
    print('You got full marks!')
    key = hashlib.sha512(answers.encode()).digest()
    flag = bytes([f ^^ k for f, k in zip(flag_enc, key)]).decode()
    print(flag)
else:
    print('Wrong!')
