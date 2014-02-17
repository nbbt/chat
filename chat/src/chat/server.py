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

class ChatServer(object):
    """
    Simple single threaded chat server. Listens to a specific port and waits for connections.
    Broadcasts client messages to all other connected clients.
    """
    SOCKET_INDEX = 0
    ADDR_INDEX = 1
    MESSAGE_FORMAT = "[%s:%s]: %s"
    
    
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
        self._connected_clients = []

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

    def _get_connected_sockets(self):
        """
        @return: All connected sockets including server socket.
        @rtype: list<socket.socket>
        """
        return [self._server_sock] +\
                [connection[ChatServer.SOCKET_INDEX] for connection in self._connected_clients]

    def _handle_connections(self):
        """
        Handle all incoming connections.
        """
        read_sockets = self._get_read_sockets()
        for sock in read_sockets:
            if sock == self._server_sock:
                self._handle_new_client()
            else:
                self._handle_data_from_existing_client(sock)
    
    def _get_read_sockets(self):
        """
        Return sockets that are ready to read from.
        """
        read_sockets, write_sockets, error_sockets =\
                                    select.select(self._get_connected_sockets(), [], [])
        return read_sockets
    
    def _handle_data_from_existing_client(self, client_socket):
        """
        Handle data received from previously connected client.
        @param client_socket: The socket from which the data is to be received.
        @type client_socket: socket.socket
        """
        try:
            data = client_socket.recv(self.recv_buffer)
            addr = self._find_addr(client_socket)
            formatted_message = self._format_message_from_user(data, addr)
            if not data:
                raise NoDataError()
            self._broadcast_message(client_socket, formatted_message)
            print "[%s:%s] sent data\n" %self._find_addr(client_socket)
        except (socket.error, NoDataError):
            self._disconnect_client(client_socket)

    def _handle_new_client(self):
        """
        Handle new connection to the server socket.
        """
        new_client_socket, new_addr = self._server_sock.accept()
        
        self._connected_clients.append((new_client_socket, new_addr))
        self._broadcast_message(new_client_socket, self._format_connected_message(new_addr))
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
        for client_socket, _ in self._connected_clients:
            if client_socket != messaging_socket:
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
        addr = self._find_addr(client_socket)
        client_socket.close()
        self._connected_clients.remove((client_socket, addr))
        self._broadcast_message(self._server_sock, self._format_disconnected_message(addr))
        
    def _find_addr(self, client_socket):
        """
        @return: The address of the given socket or None if the socket doen't exist in connected
        clients list.
        @rtype: tuple
        """
        for socket, addr in self._connected_clients:
            if socket == client_socket:
                return addr
            
        return None
        
    def _format_message_from_user(self, message, sender_addr):
        """
        Return the message in the right format, ready for sending to the clients.
        @param message: The message to format, as received from the client.
        @type message: str.
        @param sender_addr: the address of the sender client.
        @type sender_addr: tuple<str, str>
        """
        return "[%s:%s]: " %sender_addr + message
    
    def _format_connected_message(self, addr):
        """
        Return appropriate message about the client with the given address that connected the chat.
        @param addr: The address of the user that connected to the chat.
        @type addr: (str, str)
        """
        return "[%s:%s] connected" %addr
    
    def _format_disconnected_message(self, addr):
        """
        Return appropriate message about the client with the given address that disconnected the 
        chat.
        @param addr: The address of the user that connected to the chat.
        @type addr: (str, str)
        """
        return "[%s:%s] disconnected" %addr
    
class NoDataError(Exception):
    """
    Raised when socket.recv doesn't throw exception but there is no data. Not supposed to happen but
    just in case...
    """ 
    pass

                
if __name__ == "__main__":
    ChatServer(HOST, PORT).start()
        
        