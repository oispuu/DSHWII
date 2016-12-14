'''
Created on Oct 27, 2016

@author: devel
'''

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from time import time

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

if __name__ == '__main__':
    mboard = MessageBoard()
    server_sock = ('127.0.0.1',7777)

    # Create XML_server
    server = SimpleXMLRPCServer(server_sock,
                            requestHandler=MboardRequestHandler)
    server.register_introspection_functions()

    # Register all functions of the Mboard instance
    server.register_instance(mboard)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Ctrl+C issued, terminating ...'
    finally:
        server.shutdown()       # Stop the serve-forever loop
        server.server_close()   # Close the sockets
    print 'Terminating ...'

