#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""КМЗИ. ЛР№4. Клиент-серверное приложение,
которое передает зашифрованное сообщение следующим образом:
                Текст шифруется шифром виженера.
                Зашифрованный текст шифруется AES и
                помещается в картинку,
                которая передается по сети второму клиенту,
                который в свою очередь расшифровывает.
Клиент
"""

import socket
import os

import vizh
import aes
import steg


def prepare_img(text, key_vizh, key_AES, img_cont_fname, res_img_fname):
    """шифрование текста и сокрытие его в картинке"""
    text_vizh = vizh.vizh(text, key_vizh, vizh.crypt)
    crypted = aes.AESCoder(key_AES).crypt_list(text_vizh)
    steg.hiding_to_image(img_cont_fname, crypted, res_img_fname)


def send_data(data, host, port):
    """отправка данных по сети"""
    sock = socket.socket()
    try:
        sock.connect((host, port))
        sock.send(data)
    except Exception as err:
        print("Error: {0}".format(err))

    sock.close()


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog="client", description="4th lab for cryptographic methods of "
                                   "information security. Client.")
    parser.add_argument('infFile', type=argparse.FileType(mode='rb'),
                        help="input file")
    parser.add_argument('keyVizh', type=argparse.FileType(mode='rb'),
                        help="file with key for Vizhiner cipher")
    parser.add_argument('keyAES', type=argparse.FileType(mode='rb'),
                        help="file with key for AES cipher")
    parser.add_argument('imageFile', help="image container")
    parser.add_argument('ipAddr', help="IP address for sending")
    return parser.parse_args()


def main():
    args = get_args()
    fname = '__' + args.imageFile + '.bmp'
    # подготавливем данные для отправки
    try:
        prepare_img(args.infFile.read(), args.keyVizh.read(),
                    args.keyAES.read(), args.imageFile, fname)
    except Exception as err:
        print "Can't create image with hidden and ciphered file"
        print("Error: {0}".format(err))
        return

    data_file = open(fname, 'rb')
    data = data_file.read()
    data_file.close()
    os.remove(fname)

    send_data(data, args.ipAddr, 8090)


if __name__ == "__main__":
    main()
