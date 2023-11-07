import random

def gen_verify_code():
    code = ""
    for i in range(6):
        num = random.randint(0, 9)
        code += str(num)
    return code