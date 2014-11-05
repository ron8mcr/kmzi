#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""КМЗИ. ЛР№1. Шифр Вижинера"""


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog="vizh", description="1st lab for cryptographic methods "
                                 "of information security. Vigenere cipher.")
    parser.add_argument('inFile', type=argparse.FileType(mode='rb'),
                        help="input file")
    parser.add_argument('keyFile', type=argparse.FileType(mode='rb'),
                        help="file with key")
    parser.add_argument('outFile', type=argparse.FileType(mode='wb'),
                        help="output file")
    parser.add_argument('cryptOrDecrypt', choices=['c', 'd'],
                        help="crypt or decrypt")
    return parser.parse_args()


def crypt(i, k):
    return i + k


def decrypt(i, k):
    return i - k


def vizh(input_, key, func):
    key_len = len(key)
    if key_len == 0:
        raise Exception('Vizhiner key is empty')
    return [chr(func(ord(s), ord(key[i % key_len])) % 256)
            for i, s in enumerate(input_)]


def main():
    args = get_args()
    funcs = {'c': crypt, 'd': decrypt}
    try:
        res = vizh(args.inFile.read(), args.keyFile.read(),
                   funcs[args.cryptOrDecrypt])
    except Exception as err:
        print("Error: {0}".format(err))
        return

    args.outFile.write(''.join(res))


if __name__ == "__main__":
    main()
