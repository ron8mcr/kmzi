#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


class ReceiveImage(Protocol):
    """Протокол приёма изображения по сети
    Просто принимается изображение и сохраняется на диске
    под именем ip_дата.bmp
    Имя сохранённого файла отправляется клиенту
    """
    def __init__(self, addr):
        self.addr = addr
        print 'connected: IP:', self.addr.host, 'port:', self.addr.port
        self.recieved_data = ""
        time_str = datetime.datetime.now().strftime("%d.%m.%Y_%I.%M.%S")
        self.fname = addr.host + '_' + time_str + '.bmp'

    def connectionMade(self):
        """При установке соединения отправим клиенту имя файла,
        с которым будет сохранено получаемое изображение
        """
        self.transport.write(self.fname)

    def dataReceived(self, data):
        self.recieved_data += data

    def connectionLost(self, reason):
        if self.recieved_data:
            with open(self.fname, 'w') as f:
                f.write(self.recieved_data)
            print 'received:', self.fname
        else:
            print self.addr.host, 'sent nothing'


class ReceiveImageFactory(Factory):
    def buildProtocol(self, addr):
        return ReceiveImage(addr)


if __name__ == "__main__":
    endpoint = TCP4ServerEndpoint(reactor, 8090)
    endpoint.listen(ReceiveImageFactory())
    reactor.run()
