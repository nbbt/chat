'''
Created on Jan 29, 2014

@author: anya
'''


from threading import Thread
import sys
import socket
from chat.server import HOST, PORT, RECV_BUFFER


def main():
    ADDR = (HOST, PORT)
    
    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    
    def recv():
        while True:
            data = tcpCliSock.recv(RECV_BUFFER)
            if not data: sys.exit(0)
            print data
    
    Thread(target=recv).start()
    while True:
        data = raw_input('> ')
        if not data: break
        tcpCliSock.send(data)
    
    tcpCliSock.close()


if __name__ == "__main__":
    main()