'''
Created on Jan 29, 2014

@author: anya
'''


from threading import Thread
import sys
import socket
from chat.server import HOST, PORT, RECV_BUFFER


class ChatClient(object):
    """
    Simple chat client. Connects to a chat server, prints received messages to the screen, sends
    types messages to the server.
    """
    def __init__(self, host_name, port, recv_buffer=RECV_BUFFER):
        """
        C'tor.
        @param host_name: The host to connect to.
        @type host_name: str.
        @param port: The number of port to use. 
        @type port: int.
        @param recv_buffer: Maximum bytes to receive per message. 
        @type recv_buffer: int.
        """
        self.host_name = host_name
        self.port = port
        self.recv_buffer = recv_buffer    
        self._please_close = False
        
    def start(self):
        """
        Start the client - listen to messages from the server and wait for messages typed by the
        user.
        """
        self._init_connection()
        #Do not change the order of the following lines (the first method is asynchronic but the 
        #second is synchronic.
        self._start_thread_for_user_messages()
        self._wait_for_messages_from_server()
        
    def _init_connection(self):
        """
        Initialize the connection to the server.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host_name, self.port))
        
        
    def _wait_for_messages_from_server(self):       
        """
        Wait for messages from the server and handle them.
        """ 
        while not self._please_close:
            data = self.socket.recv(RECV_BUFFER)
            if not data: 
                break
            self._handle_message_from_server(data)
        
        self._close()
        
    def _close(self):
        self._please_close = True
        self._user_message_thread.join()
        self.socket.close()

    def _handle_message_from_server(self, message):
        """
        Handle a message received from the server.
        @param message: The message to handle
        @type message: str 
        """
        print message
        
    def _start_thread_for_user_messages(self):
        """
        Start another thread to handle messages from the user.
        """
        self._user_message_thread = Thread(target=self._handle_user_messages)
        self._user_message_thread.start()
        
    def _handle_user_messages(self):
        """
        Wait for messages from the user. Send each message to the server. 
        """
        while not self._please_close:
            data = raw_input()
            if not data: 
                self._please_close = True
            else:
                self.socket.send(data)
        
    

if __name__ == "__main__":
    ChatClient(HOST, PORT).start()