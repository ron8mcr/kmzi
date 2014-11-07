#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""КМЗИ. ЛР№4. Клиент-серверное приложение,
                которое передает зашифрованное сообщение следующим образом:
                Текст шифруется шифром виженера.
                Зашифрованный текст шифруется AES и
                помещается в картинку,
                которая передается по сети второму клиенту,
                который в свою очередь расшифровывает.

Часть серверной части, отвечающая за
извлечение информации из полученного изображения
"""

import vizh
import aes
import steg


def get_args():
    import argparse
    parser = argparse.ArgumentParser(
        prog="server2", description="4th lab for cryptographic methods of "
        "information security. Extractor.")
    parser.add_argument('imgFile', help="recieved image name")
    parser.add_argument('keyVizh', type=argparse.FileType(mode='rb'),
                        help="file with key for Vizhiner cipher")
    parser.add_argument('keyAES', type=argparse.FileType(mode='rb'),
                        help="file with key for AES cipher")
    parser.add_argument('outFile', type=argparse.FileType(mode='wb'),
                        help="output file")
    return parser.parse_args()


def main():
    args = get_args()

    try:
        from_image = steg.extracting_from_image(args.imgFile)
        coder_AES = aes.AESCoder(args.keyAES.read())
        decrypted_AES = coder_AES.decrypt_list(from_image)
        res = vizh.vizh(decrypted_AES, args.keyVizh.read(), vizh.decrypt)
        args.outFile.write(''.join(res))
    except Exception as err:
        print ("Error: {0}".format(err))
        return

if __name__ == "__main__":
    main()
