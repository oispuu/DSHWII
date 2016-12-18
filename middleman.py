from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


class MiddleMan():
    def __init__(self):
        self.availableServers = []

    def notify_server_up(self, server_sock):
        print 'Added server %s' % server_sock
        self.availableServers.append(server_sock)
        return True

    def notify_server_down(self, server_sock):
        self.availableServers.remove(server_sock)
        return True

    def get_available_servers(self):
        return self.availableServers


class MboardRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

if __name__ == '__main__':
    middleman = MiddleMan()
    middleman_sock = ('127.0.0.1', 7777)

    print 'Middleman created on %s' % str(middleman_sock)

    # Create XML_server
    server = SimpleXMLRPCServer(middleman_sock,
                            requestHandler=MboardRequestHandler)
    server.register_introspection_functions()

    # Register all functions of the Mboard instance
    server.register_instance(middleman)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Ctrl+C issued, terminating ...'
    finally:
        server.shutdown()       # Stop the serve-forever loop
        server.server_close()   # Close the sockets
    print 'Terminating ...'
