'''
Created on Oct 27, 2016

@author: devel
'''
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
from argparse import ArgumentParser
from sys import stdin, exit
from xmlrpclib import ServerProxy
from time import asctime, localtime

# Constants -------------------------------------------------------------------
___NAME = 'MBoard Client'
___VER = '0.2.0.0'
___DESC = 'Simple Message Board Client (RPC version)'
___BUILT = '2016-10-27'
___VENDOR = 'Copyright (c) 2016 DSLab'

DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'

# Private methods -------------------------------------------------------------
def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)
# Not a real main method-------------------------------------------------------

def mboard_client_main(args):

    # Starting client
    LOG.info('%s version %s started ...' % (___NAME, ___VER))
    LOG.info('Using %s version %s' % ( ___NAME, ___VER))

    # Processing arguments
    # 1.) If -m was provided
    # m = ''
    # if len(args.message) > 0:
    #     m = args.message # Message to publish
    #     if m == '-':
    #         LOG.debug('Will read message from standard input ...')
    #         # Read m from STDIN
    #         m = stdin.read()
    #     LOG.debug('User provided message of %d bytes ' % len(m))
    #
    # # Processing arguments
    # # 2.) If -l was provided
    # # Parse integer
    # n = int(args.last)  # Last n messages to fetch
    # n = n if n > 0 else 0 # no negative values allowed
    # LOG.debug('Will request %s published messages'\
    #           '' % ('all' if n == 0 else ('last %d' % n)))

    # RPC Server's socket address
    server = (args.host,int(args.port))
    try:
        mm_proxy = ServerProxy("http://%s:%d" % server)
    except KeyboardInterrupt:
        LOG.warn('Ctrl+C issued, terminating')
        exit(0)
    except Exception as e:
        LOG.error('Communication error %s ' % str(e))
        exit(1)

    LOG.info('Connected to Mboard XMLRPC server!')
    methods = filter(lambda x: 'system.' not in x, mm_proxy.system.listMethods())
    LOG.debug('Remote methods are: [%s] ' % (', '.join(methods)))

    available_servers = mm_proxy.get_available_servers()
    print 'Pick a server (insert index): \n'
    j = 1
    for i in available_servers:
        print '%d. %s \n' % (j, str(i))
        j += 1

    server_choice = raw_input()
    server_choice = available_servers[int(server_choice)-1]

    print 'Server choice was %s' % str(server_choice)

    try:
        proxy = ServerProxy("http://%s:%d" % tuple(server_choice))
        LOG.info('Connected to %s' % str(server_choice))
    except KeyboardInterrupt:
        LOG.warn('Ctrl+C issued, terminating')
        exit(0)
    except Exception as e:
        LOG.error('Communication error %s ' % str(e))
        exit(1)

    ids = []
    msgs = []

    # try:
    #     if len(m) > 0:
    #         proxy.publish(m)
    #         LOG.info('Message published')
    #     # Query messages
    #     # With TCP we may get all messages in one request
    #     ids += proxy.last(n)
    # except Exception as e:
    #     LOG.error('Communication error %s ' % str(e))
    #     exit(1)
    # except KeyboardInterrupt:
    #         LOG.debug('Crtrl+C issued ...')
    #         LOG.info('Terminating ...')
    #         exit(2)
    #
    # try:
    #     msgs += map(lambda x: proxy.get(x), ids)
    # except Exception as e:
    #     LOG.error('Communication error %s ' % str(e))
    #     exit(1)
    # except KeyboardInterrupt:
    #         LOG.debug('Crtrl+C issued ...')
    #         LOG.info('Terminating ...')
    #         exit(2)
    #
    # msgs = map(lambda x: tuple(x[:3]+[' '.join(x[3:])]),msgs)
    #
    # if len(msgs) > 0:
    #     t_form = lambda x: asctime(localtime(float(x)))
    #     m_form = lambda x: '%s -> '\
    #                         '%s' % (t_form(x[0]),x[3])
    #     print 'Board published messages:'
    #     print '\n'.join(map(lambda x: m_form(x),msgs))

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
    parser.add_argument('-m','--message',\
                        help='Message to publish',\
                        default='')
    parser.add_argument('-l','--last', metavar='N', type=int,\
                        help='Get iDs of last N messages,'\
                        'defaults to "all"',\
                        default=0)
    args = parser.parse_args()
    mboard_client_main(args)