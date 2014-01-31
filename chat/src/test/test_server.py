'''
Created on Jan 30, 2014

@author: anya
'''
import unittest
from chat.server import ChatServer, HOST, PORT


class ChatServerTest(unittest.TestCase):    
    def test_handle_connections(self):
        """
        Test the method _handle_connections. Send some messages using mock clients and make
        sure all clients receive the appropriate messages.
        """
        server = MockChatServer()
        
        client1 = MockChatClient(server)
        client2 = MockChatClient(server)
        client3 = MockChatClient(server)
        
        #Handle the connections one by one because the MockServer doesn't support a queue of 
        #connections.
        client1.connect()
        server._handle_connections()
        client2.connect()
        server._handle_connections()
        client3.connect()
        server._handle_connections()
        
        data1, data2, data3, data4 = "1", "2", "3", "4"
        client1.send_data(data1)
        client2.send_data(data2)
        client3.send_data(data3)
        client2.send_data(data4)
        
        server._handle_connections()
        
        self.assertIn(data2, client1.received_data)
        self.assertIn(data3, client1.received_data)
        self.assertIn(data4, client1.received_data)
        self.assertNotIn(data1, client1.received_data, "Client shouldn't receive its one messages.")

        self.assertIn(data1, client2.received_data)
        self.assertIn(data3, client2.received_data)
        self.assertNotIn(data2, client2.received_data, "Client shouldn't receive its one messages.")
        self.assertNotIn(data4, client2.received_data, "Client shouldn't receive its one messages.")
        
        self.assertIn(data1, client3.received_data)
        self.assertIn(data2, client3.received_data)
        self.assertIn(data4, client3.received_data)
        self.assertNotIn(data3, client3.received_data, "Client shouldn't receive its one messages.")

class MockChatServer(ChatServer):
    """
    Mock chat server for tests. Overrides methods using sockets.
    """
    
    def __init__(self):
        ChatServer.__init__(self, HOST, PORT)
        self._init_connections()
    
    def _init_connections(self):
        self._server_sock = MockSocket()
        self._connection_list = []
        self.read_sockets = []
        
    def _get_read_sockets(self):
        return self.read_sockets
    
    def add_read_socket(self, socket):
        self.read_sockets.append(socket)
        
    def add_accepted_connection(self, accepted_socket):
        self._server_sock.accepted_socket = accepted_socket
        self.read_sockets.append(self._server_sock)
                
        
class MockChatClient(object):
    """
    Mock chat client. Simulates the behavior of a client without using MockSockets.
    """
    def __init__(self, mock_server):
        self.mock_server = mock_server
        self.pair_socket = MockSocket()
        self.client_socket, self.server_socket = MockSocket.create_pair_sockets()
         
    def connect(self):
        self.mock_server.add_accepted_connection(self.server_socket)
        
    def send_data(self, data):
        self.client_socket.send(data)
        self.mock_server.add_read_socket(self.server_socket)
        
    @property    
    def received_data(self):
        """
        @return: The data that was received by the client.
        @rtype: list<str>
        """
        return self.client_socket.received_data
        
        
      
class MockSocket(object):
    """
    Mock object to simulate a socket. Saves all data 'sent' in a list. Returns predetermined data
    when recv is called.
    If you want to simulate "peer to peer" - use the static method create_pair_sockets to create 
    2 sockets - the data that is sent by one is received by the other.
    """
    
    FAKE_ADDR = (1,1)
    
    def __init__(self):
        self.received_data = []
        self.sent_data = []
        self.closed = False
        self.accepted_socket = None

    def send(self, data):
        self.sent_data.append(data)
    
    def recv(self, recv_buffer):
        return self.received_data.pop()
        
    def add_received_data(self, data):
        self.received_data.append(data)
    
    def close(self):
        self.closed = True        
        
    def accept(self):
        return (self.accepted_socket, MockSocket.FAKE_ADDR)
        

    @staticmethod
    def create_pair_sockets():
        """
        Return 2 sockets that simulate "peer to peer" - the data you send to one of them is added
        to the 'received_list" of the other.
        """
        socket1 = MockSocket()
        socket2 = MockSocket()      
        socket1.received_data = socket2.sent_data
        socket2.received_data = socket1.sent_data
        return socket1, socket2

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()