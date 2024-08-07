import math

def encode_permutation_to_7_bits(permutation):
    n = len(permutation)
    bits = 0
    unused = [True] * n
    for i in range(n - 1):
        count = 0
        current = permutation[i]
        for j in range(n):
            if unused[j] and j < current:
                count += 1
        bits += count * math.factorial(n - i - 1)
        unused[current] = False
    return bits

LEVELS = bytes.fromhex('02 04 01 00 03 03 02 00 04 01 02 04 00 03 01 03 02 00 01 04 02 04 03 00 01 00 01 03 04 02 00 01 02 04 03 02 00 01 03 04 04 03 01 02 00 03 04 02 01 00 04 00 01 03 02 04 03 00 01 02 02 00 03 04 01 03 04 02 01 00 04 01 00 03 02 02 00 01 03 04 02 00 01 03 04 04 00 03 01 02 03 04 02 01 00 04 00 01 03 02 04 03 01 00 02 03 04 02 01 00 04 02 03 00 01 04 03 00 01 02 02 00 03 04 01 04 03 00 02 01 04 03 00 02 01 04 01 02 03 00 04 02 01 00 03 04 01 00 03 02 03 04 02 01 00 04 00 02 01 03 04 03 01 02 00 04 03 01 00 02 04 03 01 00 02 02 00 01 03 04 04 02 01 00 03 04 03 00 02 01 03 04 02 01 00 00 01 03 02 04 02 01 03 00 04 00 01 02 04 03 02 00 03 01 04 04 01 02 00 03 00 01 03 02 04 04 01 03 00 02 04 00 02 01 03 00 01 02 03 04 02 00 01 03 04 00 01 02 04 03 02 01 00 04 03 00 01 02 03 04 00 01 02 04 03 02 00 01 04 03 02 01 03 04 00 04 00 01 03 02 04 02 00 01 03 04 00 03 02 01 04 03 02 01 00 04 02 03 00 01 02 01 03 00 04 00 01 03 02 04 02 01 03 04 00 00 01 02 03 04 02 00 01 03 04 02 00 01 04 03 04 02 03 00 01 04 03 02 00 01 00 01 03 02 04 04 02 03 01 00 02 01 03 04 00 00 01 02 03 04 00 01 02 04 03 00 01 04 03 02 00 00')

levels = []
for i in range(0, len(LEVELS), 5):
    levels.append(list(LEVELS[i:i+5]))

for l in levels:
    c = encode_permutation_to_7_bits(l)
    if c < 0x20:
        c += 120
    print(chr(c), end='')
print()
