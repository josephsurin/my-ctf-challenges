import ast, hashlib
from string import ascii_letters


def solve_q1(given):
    c = given

    # TODO: solve q1

    return ''


def solve_q2(given):
    n, e, c = given

    # TODO: solve q2

    return ''


def solve_q3(given):
    n, e, c = given

    # TODO: solve q3

    return ''


def solve_q4(given):
    g, p, c = given

    # TODO: solve q4

    return ''


def solve_q5(given):
    g, p, c = given

    # TODO: solve q5

    return ''


def solve_q6(given):
    p, a, b, Py = given

    # TODO: solve q6

    return ''


dat = open('./output.txt', 'r').readlines()
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
    flag = bytes([f ^ k for f, k in zip(flag_enc, key)]).decode()
    print(flag)
else:
    print('Wrong!')
