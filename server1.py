#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""КМЗИ. ЛР№4. Клиент-серверное приложение,
                которое передает зашифрованное сообщение следующим образом:
                Текст шифруется шифром виженера.
                Зашифрованный текст шифруется AES и
                помещается в картинку,
                которая передается по сети второму клиенту,
                который в свою очередь расшифровывает.

часть серверной части, отвечающая за приём изображений от клиентов достуточно
тупая, только принимает изображения от клиентов и сохраняет их на диске.
Вытаскивание из них необходимой информации - другой разговор (server2.py)
"""

import socket
import datetime
import threading


def session(conn, addr):
    print 'connected: IP:', addr[0], 'port:', addr[1]
    conn.settimeout(10)
    res = ""
    while True:
        try:
            data = conn.recv(1000000)
        except Exception as err:
            print 'connection', addr, "error: {0}".format(err)
            conn.close()
            return

        if not data:
            break
        res += data
    conn.close()

    if res:
        time_str = datetime.datetime.now().strftime("%d.%m.%Y_%I.%M.%S")
        fname = addr[0] + '_' + time_str + '.bmp'
        with open(fname, 'wb') as out_file:
            out_file.write(res)
        print 'received:', fname
    else:
        print addr, 'is send nothing'

    return


def main():
    sock = socket.socket()
    port = 8090
    try:
        sock.bind(('', port))
    except Exception as err:
        print ("Error: {0}".format(err))
        return

    sock.listen(100)
    while True:
        conn, addr = sock.accept()
        th = threading.Thread(name='th1', target=session, args=(conn, addr))
        th.start()

if __name__ == "__main__":
    main()
