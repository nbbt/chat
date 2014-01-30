'''
Created on Jan 29, 2014

@author: anya
'''
import socket
import select


HOST = socket.gethostname()
PORT = 14791
BACKLOG = 5
RECV_BUFFER = 4096 

def broadcast_message(sock, message, connection_list, server_sock):
    for s in connection_list:
        if s != sock and s != server_sock:
            try:
                s.send(message)
            except:
                s.close()
                connection_list.remove(s)
            
def main():
    server_sock = socket.socket()
    server_sock.bind((HOST, PORT))
    server_sock.listen(BACKLOG)
    
    connection_list = [server_sock]
    
    while True:
        read_sockets,write_sockets,error_sockets = select.select(connection_list,[],[])
        
        for sock in read_sockets:
            if sock == server_sock:
                client_socket, addr = server_sock.accept()
                connection_list.append(client_socket)
                broadcast_message(client_socket, "[%s:%s] entered room\n" % addr, connection_list, server_sock)
                print "[%s:%s] connected\n" % addr
            else:
                data = sock.recv(RECV_BUFFER)
                if data:
                    broadcast_message(sock, data, connection_list, server_sock)
                    print "[%s:%s] sent data\n" % addr
                    
                
                
if __name__ == "__main__":
    main()        
    
        
        