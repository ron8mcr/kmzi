#!/usr/bin/python
# -*- coding: UTF-8 -*-

# КМЗИ. ЛР№1. Шифр Вижинера
def getArgs():
    import argparse

    parser = argparse.ArgumentParser(prog="vizh",
                                     description="1st lab for cryptographic methods of information security. Vigenere cipher.")
    parser.add_argument('inFile', type=argparse.FileType(mode='rb'), help="input file")
    parser.add_argument('keyFile', type=argparse.FileType(mode='rb'), help="file with key")
    parser.add_argument('outFile', type=argparse.FileType(mode='wb'), help="output file")
    parser.add_argument('cryptOrDecrypt', choices=['c', 'd'], help="crypt or decrypt")
    return parser.parse_args()


def c(i, k):
    return i + k


def d(i, k):
    return i - k


def vizh(inputList, keyList, func):
    if len(keyList) == 0:
        raise Exception, 'Vizhiner key is empty'
    return [chr(func(ord(item[1]), ord(keyList[item[0] % len(keyList)])) % 256) for item in list(enumerate(inputList))]


def main():
    args = getArgs()
    try:
        res = vizh(list(args.inFile.read()), list(args.keyFile.read()), eval(args.cryptOrDecrypt))
    except Exception as err:
        print("Error: {0}".format(err))
        return

    args.outFile.write(''.join(res))


if __name__ == "__main__":
    main()
