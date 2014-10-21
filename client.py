#!/usr/bin/python
# -*- coding: UTF-8 -*-

# КМЗИ. ЛР№4. Клиент-серверное приложение,
# которое передает зашифрованное сообщение следующим образом:
#                Текст шифруется шифром виженера.
#                Зашифрованный текст шифруется AES и 
#                помещается в картинку, 
#                которая передается по сети второму клиенту, 
#                который в свою очередь расшифровывает.
# Клиент

import vizh
import aes
import steg
import socket
import os


def prepareIMG(text, keyVizh, keyAES, imgContFName):
    """шифрование текста и сокрытие его в картинке"""
    textV = vizh.vizh(text, keyVizh, vizh.crypt)
    coderAES = aes.aesCoder(keyAES)
    crypted, nZeroes = coderAES.cryptList(textV)
    toHide = [chr(nZeroes)] + crypted
    outImg = steg.hidingToImage(imgContFName, toHide)
    return outImg


def sendData(data, host, port):
    """отправка данных по сети"""
    sock = socket.socket()
    try:
        sock.connect((host, port))
        sock.send(data)
    except Exception as err:
        print("Error: {0}".format(err))

    sock.close()


def getArgs():
    import argparse

    parser = argparse.ArgumentParser(prog="client",
                                     description="4th lab for cryptographic methods of information security. Client.")
    parser.add_argument('infFile', type=argparse.FileType(mode='rb'), help="input file")
    parser.add_argument('keyVizh', type=argparse.FileType(mode='rb'), help="file with key for Vizhiner cipher")
    parser.add_argument('keyAES', type=argparse.FileType(mode='rb'), help="file with key for AES cipher")
    parser.add_argument('imageFile', help="image container")
    parser.add_argument('ipAddr', help="IP address for sending")
    return parser.parse_args()


def main():
    args = getArgs()

    # подготавливем данные для отправки
    try:
        img = prepareIMG(list(args.infFile.read()), list(args.keyVizh.read()), list(args.keyAES.read()), args.imageFile)
    except Exception as err:
        print "Can't create image with hidden and ciphered file"
        print("Error: {0}".format(err))
        return

    fName = '__' + args.imageFile + '.bmp'
    img.save(fName, "BMP")
    #img.close()
    dataFile = open(fName, 'rb')
    data = dataFile.read()
    dataFile.close()
    os.remove(fName)

    sendData(data, args.ipAddr, 8090)


if __name__ == "__main__":
    main()
