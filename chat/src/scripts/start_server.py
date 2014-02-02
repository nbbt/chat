'''
Created on Feb 2, 2014

@author: anya
'''
from optparse import OptionParser
from chat.server import PORT, HOST, ChatServer


def get_option_parser():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", type="int",
                      help="The port to listen on", default=PORT)
    return parser

if __name__ == "__main__":
    (options, args) = get_option_parser().parse_args()
    print "Starting server, using port %d" %(options.port)
    ChatServer(HOST, options.port).start()