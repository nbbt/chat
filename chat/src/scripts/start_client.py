'''
Created on Feb 2, 2014

@author: anya
'''
from optparse import OptionParser
from chat.server import PORT, HOST
from chat.client import ChatClient


def get_option_parser():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", type="int",
                      help="The post to connect to", default=PORT)
    return parser

if __name__ == "__main__":
    (options, args) = get_option_parser().parse_args()
    print "Starting client, using port %d" %(options.port)
    ChatClient(HOST, options.port).start()