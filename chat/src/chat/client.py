'''
Created on Jan 29, 2014

@author: anya
'''


from threading import Thread
import sys
import socket


def main():
    HOST = socket.gethostname()
    PORT = 14791
    BUFSIZE = 4096
    ADDR = (HOST, PORT)
    
    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    
    def recv():
        while True:
            data = tcpCliSock.recv(BUFSIZE)
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