import os, random

FLAG = os.getenv('FLAG', 'oiccflag{????????????????????????????????????????}').encode()
FLAG = FLAG[9:-1]
assert len(FLAG) == 40

v = {}
v['🚩'] = FLAG
v['🍆'] = 4551037765311920851 # random 64 bit prime
v['🍔'] = int.from_bytes(v['🚩'][:8], 'big')
v['🍣'] = int.from_bytes(v['🚩'][8:16], 'big')
v['🍌'] = int.from_bytes(v['🚩'][16:24], 'big')
v['🍫'] = int.from_bytes(v['🚩'][24:32], 'big')
v['🍊'] = int.from_bytes(v['🚩'][32:40], 'big')
v['🙈'] = random.randrange(0, 2**4)
v['🙉'] = random.randrange(0, 2**4)
v['🙊'] = random.randrange(0, 2**4)
v['🐶'] = random.randrange(0, 2**4)
v['🐻'] = random.randrange(0, 2**4)

print((v['🍔']**7  + v['🍣']**7  + v['🍌']**7  + v['🍫']**7  + v['🍊']**7  + v['🙈']) % v['🍆'])
print((v['🍔']**14 + v['🍣']**14 + v['🍌']**14 + v['🍫']**14 + v['🍊']**14 + v['🙉']) % v['🍆'])
print((v['🍔']**21 + v['🍣']**21 + v['🍌']**21 + v['🍫']**21 + v['🍊']**21 + v['🙊']) % v['🍆'])
print((v['🍔']**28 + v['🍣']**28 + v['🍌']**28 + v['🍫']**28 + v['🍊']**28 + v['🐶']) % v['🍆'])
print((v['🍔']**35 + v['🍣']**35 + v['🍌']**35 + v['🍫']**35 + v['🍊']**35 + v['🐻']) % v['🍆'])
