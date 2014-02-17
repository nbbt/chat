'''
Created on Jan 30, 2014

@author: anya
'''
import unittest
from chat.server import ChatServer, HOST, PORT

FAKE_ADDR = ("1.2.3.4", "8456")

class ChatServerTest(unittest.TestCase):    

    def setUp(self):
        self.server = MockChatServer()
        
        self.addr1 = ("1.2.3.4", "8888")
        self.addr2 = ("2.3.4.5", "9999")
        self.addr3 = ("3.4.5.6", "7777")
        self.client1 = MockChatClient(self.server, self.addr1)
        self.client2 = MockChatClient(self.server, self.addr2)
        self.client3 = MockChatClient(self.server, self.addr3)

        #Handle the connections one by one because the MockServer doesn't support a queue of 
        #connections.
        self.client1.connect()
        self.server._handle_connections()
        self.client2.connect()
        self.server._handle_connections()
        self.client3.connect()
        self.server._handle_connections()

    def test_connection_messages(self):
        """
        Check that clients are informed other clients that connect the chat.
        """        
        expected_messages_client1 = [self.server._format_connected_message(self.addr2),
                                     self.server._format_connected_message(self.addr3)]
        expected_messages_client2 = [self.server._format_connected_message(self.addr3)]
        expected_messages_client3 = []
        self.assertSequenceEqual(expected_messages_client1, self.client1.received_data,\
                            "Clients should receive notification about new connections.")
        self.assertSequenceEqual(expected_messages_client2, self.client2.received_data,\
                            "Clients should receive notification about new connections.")
        self.assertSequenceEqual(expected_messages_client3, self.client3.received_data,\
                            "Client connected last, should receive any connection notifications.")        
    
    def test_messages_distributed(self):
        """
        Check that when a client sends a message it is distributed to all other connected clients.
        """        
        data1, data2, data3, data4 = "1", "2", "3", "4"
        self.client1.send_data(data1)
        self.client2.send_data(data2)
        self.client3.send_data(data3)
        self.client2.send_data(data4)
        
        self.server._handle_connections()
        
        #Expected messages without new user connection messages:
        expected_msgs1 = [self.server._format_message_from_user(data2, self.addr2),
                              self.server._format_message_from_user(data3, self.addr3),
                              self.server._format_message_from_user(data4, self.addr2)]
        
        expected_msgs2 = [self.server._format_message_from_user(data1, self.addr1),
                              self.server._format_message_from_user(data3, self.addr3)]
        
        expected_msgs3 = [self.server._format_message_from_user(data1, self.addr1),
                              self.server._format_message_from_user(data2, self.addr2),
                              self.server._format_message_from_user(data4, self.addr2)]  
        
        
        self._remove_connectiong_messages()
        
        self.assertSequenceEqual(expected_msgs1, self.client1.received_data,
                        "Client should get all messages the other clients sent")
        self.assertSequenceEqual(expected_msgs2, self.client2.received_data,
                        "Client should get all messages the other clients sent")        
        self.assertSequenceEqual(expected_msgs3, self.client3.received_data,
                        "Client should get all messages the other clients sent")
        
    def test_recv_throws_exception(self):
        """
        Check that if while trying to receive a message from the client exception is thrown,
        the server doesn't crash and keeps working normally.
        """
        def bad_recv(self, message):
            raise Exception()
        
        self.client1.server_socket.recv = bad_recv
        message = "Hi"
        self.client2.send_data(message)
        self.server._handle_connections()
        self.assertIn(self.server._format_message_from_user(message, self.addr2),
                      self.client3.received_data,
                      "Clients should still get messages after one of the disconnects.")
        
    def test_recv_returns_none(self):
        """
        Check that if while trying to receive a message from the client None is returned,
        the server doesn't crash and keeps working normally.
        """
        def bad_recv(self, message):
            return None
        
        self.client1.server_socket.recv = bad_recv
        message = "Hi"
        self.client2.send_data(message)
        self.server._handle_connections()
        self.assertIn(self.server._format_message_from_user(message, self.addr2),
                      self.client3.received_data,
                      "Clients should still get messages after one of the disconnects.")

    def test_send_throws_exception(self):
        """
        Check that if it it possible to send a message to one client the server doesn't crash and 
        keeps working normally.
        """
        def bad_send(self, message):
            raise Exception()
        
        self.client1.server_socket.send = bad_send
        message = "Hi"
        self.client2.send_data(message)
        self.server._handle_connections()
        self.assertIn(self.server._format_disconnected_message(self.addr1),
                      self.client2.received_data,
                      "Clients should get message about other clients disconnection.")
        self.assertIn(self.server._format_message_from_user(message, self.addr2),
                      self.client3.received_data,
                      "Clients should still get messages after one of the disconnects.")


    
    def _remove_connectiong_messages(self):
        """
        Remove all new user connections messages from the received messages (by the clients).
        @param msgs_lst: The message list to process.
        """
        connection_msgs = [self.server._format_connected_message(self.addr1),
                              self.server._format_connected_message(self.addr2),
                              self.server._format_connected_message(self.addr3)]
        self.client1.set_received_data(
                    self._remove_from_lst(self.client1.received_data, connection_msgs))
        self.client2.set_received_data(
                    self._remove_from_lst(self.client2.received_data, connection_msgs))
        self.client3.set_received_data(
                    self._remove_from_lst(self.client3.received_data, connection_msgs))
        
    def _remove_from_lst(self, lst, elemets):
        """
        Return a new list that is like the old list after removing all given elements. 
        """
        return filter(lambda x: x not in elemets, lst)
        
            

class MockChatServer(ChatServer):
    """
    Mock chat server for tests. Overrides methods using sockets.
    """
    
    def __init__(self):
        ChatServer.__init__(self, HOST, PORT)
        self._init_connections()
    
    def _init_connections(self):
        self._server_sock = MockSocket()
        self.read_sockets = []
        
    def _get_read_sockets(self):
        read_sockets = self.read_sockets
        self.read_sockets = []
        return read_sockets
    
    def add_read_socket(self, socket):
        self.read_sockets.append(socket)
        
    def add_accepted_connection(self, accepted_socket):
        self._server_sock.accepted_socket = accepted_socket
        self.read_sockets.append(self._server_sock)
                
        
class MockChatClient(object):
    """
    Mock chat client. Simulates the behavior of a client without using MockSockets.
    """
    
    def __init__(self, mock_server, addr=None):
        addr = addr or FAKE_ADDR
        self.mock_server = mock_server
        self.client_socket, self.server_socket = MockSocket.create_pair_sockets(addr)
         
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
    
    def set_received_data(self, received_data):
        self.client_socket.received_data = received_data
        
      
class MockSocket(object):
    """
    Mock object to simulate a socket. Saves all data 'sent' in a list. Returns predetermined data
    when recv is called.
    If you want to simulate "peer to peer" - use the static method create_pair_sockets to create 
    2 sockets - the data that is sent by one is received by the other.
    """
        
    def __init__(self, addr=FAKE_ADDR):
        self.received_data = []
        self.sent_data = []
        self.closed = False
        self.accepted_socket = None
        self.addr = addr or FAKE_ADDR

    def send(self, data):
        self.sent_data.append(data)
    
    def recv(self, recv_buffer):
        return self.received_data.pop(0)
        
    def add_received_data(self, data):
        self.received_data.append(data)
    
    def close(self):
        self.closed = True        
        
    def accept(self):
        return (self.accepted_socket, self.accepted_socket.addr)
        

    @staticmethod
    def create_pair_sockets(addr):
        """
        Return 2 sockets that simulate "peer to peer" - the data you send to one of them is added
        to the 'received_list" of the other.
        
        @param addr: the address for the sockets. For simplicity both sockets get the same address.
        @type addr: (str, str)
        """
        socket1 = MockSocket(addr)
        socket2 = MockSocket(addr)      
        socket1.received_data = socket2.sent_data
        socket2.received_data = socket1.sent_data
        return socket1, socket2

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()