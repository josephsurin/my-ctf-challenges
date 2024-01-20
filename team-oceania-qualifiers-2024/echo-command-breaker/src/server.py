#!/usr/bin/env python3

import os
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES


KEY = os.urandom(16)
FLAG = os.getenv('FLAG', 'oiccflag{test_flag}')
FORBIDDEN = '"\\\'=+-*/()[]._#in\n\r'


def encrypt(msg):
    aes = AES.new(KEY, AES.MODE_ECB)
    return aes.encrypt(pad(msg.encode(), 16))


def decrypt(ct):
    aes = AES.new(KEY, AES.MODE_ECB)
    return unpad(aes.decrypt(ct), 16).decode()


def menu():
    print('1. Generate echo command')
    print('2. Use command')
    return int(input('> '))


def main():
    while True:
        option = menu()
        if option == 1:
            words = input('Enter your words to say: ')
            if len(words) > 14 or any(c in words for c in FORBIDDEN):
                print('Invalid words!')
                continue
            ct = encrypt(f'print("{words}")')
            print('Encrypted echo command:', ct.hex())
        elif option == 2:
            enc_cmd = bytes.fromhex(input('Enter your encrypted command: '))
            cmd = decrypt(enc_cmd)
            exec(cmd)
        else:
            print('Invalid choice!')


if __name__ == '__main__':
    main()
