'''
Created on Jan 29, 2014

@author: anya
'''
import socket
import select

HOST = socket.gethostname()
PORT = 14792
BACKLOG = 5
RECV_BUFFER = 4096 

class ChatServer(object):
    """
    Simple single threaded chat server. Listens to a specific port and waits for connections.
    Broadcasts client messages to all other connected clients.
    """
    def __init__(self, host_name, port, recv_buffer=RECV_BUFFER, backlog=BACKLOG):
        """
        C'tor.
        @param host_name: The host to start the server on.
        @type host_name: str.
        @param port: The number of port t use. 
        @type port: int.
        @param recv_buffer: Maximum bytes to receive per message. 
        @type recv_buffer: int.
        @param backlog: Maximum number of queued connection.
        @type backlog: int.
        """
        self.host_name = host_name
        self.port = port
        self.recv_buffer = recv_buffer
        self.backlog = backlog

    def start(self):
        """
        Start the server - make it listen to the given port and wait for connections.
        """
        self._init_connections()
        while True:
            self._handle_connections()
            
    def _init_connections(self): 
        """
        Prepare to receive incoming connections. Initialize all relevant memebers.
        """
        self._server_sock = socket.socket()
        self._server_sock.bind((self.host_name, self.port))
        self._server_sock.listen(BACKLOG)
        self._connection_list = [self._server_sock]

    def _handle_connections(self):
        """
        Handle all incoming connections.
        """
        read_sockets, write_sockets, error_sockets = select.select(self._connection_list, [], [])
        for sock in read_sockets:
            if sock == self._server_sock:
                self._handle_new_client()
            else:
                self._handle_data_from_existing_client(sock)
    
    def _handle_data_from_existing_client(self, client_socket):
        """
        Handle data received from previously connected client.
        @param client_socket: The socket from which the data is to be received.
        @type client_socket: socket.socket
        """
        data = client_socket.recv(self.recv_buffer)
        if data:
            self._broadcast_message(client_socket, data)
            print "[] sent data\n" 

    def _handle_new_client(self):
        """
        Handle new connection to the server socket.
        """
        new_client_socket, new_addr = self._server_sock.accept()
        
        self._connection_list.append(new_client_socket)
        self._broadcast_message(new_client_socket, "[%s:%s] entered room\n" %new_addr)
        print "[%s:%s] connected\n" % new_addr

    def _broadcast_message(self, messaging_socket, message):
        """
        Send the message to all clients except the one the the messaging_socket belongs to.
        @param messaging_socket: the socket the message was received from and should not be
        sent to.
        @type messaging_socket: socket.socket.
        @param message: The message to broadcats.
        @type message: str.
        """
        for client_socket in self._connection_list:
            if client_socket != messaging_socket and client_socket != self._server_sock:
                self._send_to_client(client_socket, message)
                
    def _send_to_client(self, client_socket, message):
        """
        Send message to specific client.
        @param client_socket: the socket to send the message to.
        @type client_socket: socket.socket.
        @param message: The message to send.
        @type message: str. 
        """
        try:
            client_socket.send(message)
        except:
            self._disconnect_client(client_socket)
                
    def _disconnect_client(self, client_socket):
        """
        Disconnect specific client.
        @param client_socket: the socket of the client to disconnect.  
        @type client_socket: socket.socket.
        """
        client_socket.close()
        self._connection_list.remove()
                
if __name__ == "__main__":
    ChatServer(HOST, PORT).start()
    
        
        