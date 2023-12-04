from random import random

def gen_hex():
    hex_code = str(hex(int(random() * 0xFFFFFF))).split("x")[1]

    if len(hex_code) < 6:
        hex_code = ("0" * (6 - len(hex_code))) + hex_code

    return "0x" + hex_code
