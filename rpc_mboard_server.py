'''
Created on Oct 27, 2016

@author: devel
'''

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from time import time
from xmlrpclib import ServerProxy
from argparse import ArgumentParser

___NAME = 'MBoard Client'
___VER = '0.2.0.0'
___DESC = 'Simple Message Board Client (RPC version)'
___BUILT = '2016-10-27'
___VENDOR = 'Copyright (c) 2016 DSLab'

DEFAULT_SERVER_PORT = 7778
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'

def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)


class MessageBoard():

    def __init__(self):
        self.__m_board = {} # For storing published messages
        self.__m_uuid = 0   # For generating unique iDs

    def __get_uuid(self):
        uuid = self.__m_uuid
        self.__m_uuid += 1
        return uuid

    def publish(self,msg,source=('',-1)):
        ip,port = source
        t = time()
        uuid = self.__get_uuid()
        self.__m_board[uuid] = (uuid, t, ip, port, msg)
        return uuid

    def last(self,n=0):
        ids = map(lambda x: x[:2], self.__m_board.values())
        ids.sort(key=lambda x: x[1])
        return map(lambda x: x[0],ids[n*-1:])

    def get(self,m_id):
        return self.__m_board[m_id][1:]

# Restrict to a particular path.
class MboardRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def mboard_server_main(args):
    mboard = MessageBoard()
    server_sock = (str(args.host), int(args.port))

    print 'Server created on %s' % str(server_sock)

    # Create XML_server
    server = SimpleXMLRPCServer(server_sock,
                            requestHandler=MboardRequestHandler)
    server.register_introspection_functions()

    # get to middleman
    mm_server = ('127.0.0.1', 7777)
    try:
        middleman = ServerProxy("http://%s:%d" % mm_server)
        print 'Got middleman up'
    except KeyboardInterrupt:
        print 'Ctrl+C issued, terminating'
        exit(0)
    except Exception as e:
        print 'Communication error %s ' % str(e)
        exit(1)

    result = middleman.notify_server_up(server_sock)

    if result:
        print 'Notified middleman'

    # Register all functions of the Mboard instance
    server.register_instance(mboard)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Ctrl+C issued, terminating ...'
    finally:
        middleman.notify_server_down(server_sock)
        server.shutdown()       # Stop the serve-forever loop
        server.server_close()   # Close the sockets
    print 'Terminating ...'

if __name__ == '__main__':
    parser = ArgumentParser(description=__info(),
                            version = ___VER)
    parser.add_argument('-H','--host',\
                        help='Server INET address '\
                        'defaults to %s' % DEFAULT_SERVER_INET_ADDR, \
                        default=DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p','--port', type=int,\
                        help='Server TCP port, '\
                        'defaults to %d' % DEFAULT_SERVER_PORT, \
                        default=DEFAULT_SERVER_PORT)
    args = parser.parse_args()
    mboard_server_main(args)
