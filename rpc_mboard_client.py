'''
Created on Oct 27, 2016

@author: devel
'''
import logging
from collections import OrderedDict

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()
from argparse import ArgumentParser
from sys import stdin, exit
from xmlrpclib import ServerProxy
from time import asctime, localtime, sleep
from tabulate import tabulate

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
    LOG.info('Using %s version %s' % (___NAME, ___VER))

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
    server = (args.host, int(args.port))
    has_joined_game = False
    try:
        mm_proxy = ServerProxy("http://%s:%d" % server)
    except KeyboardInterrupt:
        LOG.warn('Ctrl+C issued, terminating')
        exit(0)
    except Exception as e:
        LOG.error('Communication error %s ' % str(e))
        exit(1)

    available_servers = mm_proxy.get_available_servers()
    if available_servers:
        print 'Pick a server (insert index): \n'
        j = 1
        for i in available_servers:
            print '%d. %s \n' % (j, str(i))
            j += 1
        server_choice = raw_input()
        server_choice = available_servers[int(server_choice) - 1]

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

        LOG.info('Connected to Mboard XMLRPC server!')
        methods = filter(lambda x: 'system.' not in x, proxy.system.listMethods())
        LOG.debug('Remote methods are: [%s] ' % (', '.join(methods)))

        nickname = raw_input('Please enter a nickname: ')
        try:
            game_servers = proxy.get_game_servers()
            OrderedDict(sorted(game_servers.items(), key=lambda t: t[0]))
            if game_servers:
                j = 1
                print 'The available game servers are: '
                for i in game_servers.keys():
                    print '%d. %s' % (j, i)
                    for k in game_servers[str(i)]:
                        print '%s' % str(k)
                    j += 1
            else:
                print 'No game servers available!'
            game_choice = raw_input('Insert server index or press 0 to create a new game server: ')

            if int(game_choice) == 0:
                server_name = raw_input('What would you like to call the server: ')
                board_setup = None
                board_width = raw_input('Enter desired board width (min 5): ')
                board_height = raw_input('Enter desired board height (min 5): ')
                if proxy.create_game_server(server_name, nickname, board_width, board_height):
                    print 'Created new server %s' % str(server_name)

                    boats = proxy.get_boats(server_name, nickname)
                    while boats:
                        selected_boat = raw_input("Select boat type (" + str(boats.keys()) + "): ")

                        if selected_boat.isdigit() and int(selected_boat) < len(boats.keys()):
                            selected_boat = boats.keys()[int(selected_boat)]

                        orientation = raw_input("Select orientation (horizontal, vertical) or (h, v): ")

                        if orientation == "h":
                            orientation = "horizontal"
                        elif orientation == "v":
                            orientation = "vertical"

                        start_x = int(raw_input("Select starting X coordinate (1-10): "))
                        while start_x + boats[selected_boat] - 1 > 10 and orientation == "vertical":
                            print("Invalid X coordinate, try again")
                            start_x = int(raw_input("Select starting X coordinate (1-10): "))

                        start_y = int(raw_input("Select starting Y coordinate (1-10): "))
                        while start_y + boats[selected_boat] - 1 > 10 and orientation == "horizontal":
                            print("Invalid Y coordinate, try again")
                            start_y = int(raw_input("Select starting Y coordinate (1-10): "))

                        checks_out = False
                        while not checks_out:
                            checks_out = proxy.check_position(server_name, selected_boat, orientation, start_x, start_y)
                            if not checks_out:
                                print("Place already taken, try again")
                                start_x = int(raw_input("Select starting X coordinate (1-10): "))
                                start_y = int(raw_input("Select starting Y coordinate (1-10): "))

                        if board_setup:
                            board_setup = proxy.set_up_board(server_name, nickname, selected_boat, orientation, start_x,
                                                             start_y, board_setup)
                        else:
                            board_setup = proxy.set_up_board(server_name, nickname, selected_boat, orientation, start_x,
                                                             start_y)
                        print(tabulate(board_setup))
                        del boats[selected_boat]
                    print 'Waiting for other players...'
                    while True:
                        has_joined_game = server_name
                        sleep(3)
                        players_ready = proxy.get_players_in_session(server_name)
                        if len(players_ready) >= 3:
                            start = raw_input('Start game? (Y/n): ')
                            if start.lower() == "y":
                                start = proxy.start_game(server_name, nickname)
                                if start:
                                    my_turn, connected, hit = proxy.poll_my_turn(server_name, nickname)
                                    while connected:
                                        if my_turn:
                                            opponents = proxy.choose_opponents(server_name, nickname)
                                            print str(opponents)
                                            opponent_choice = False
                                            while not isinstance(opponent_choice, int):
                                                opponent_choice = raw_input('Choose opponent (1-%d)' % len(opponents))
                                                opponent_choice = int(opponent_choice) - 1
                                                if opponent_choice > len(opponents) - 1 or opponent_choice < 0:
                                                    print 'That is not an option.'
                                                    opponent_choice = False
                                            coordX = raw_input('Choose X coordinate: ')
                                            coordY = raw_input('Choose Y coordinate: ')
                                            coordX = int(coordX)
                                            coordY = int(coordY)

                                            shot_success = proxy.validate_shot(server_name, nickname, opponent_choice, coordX,
                                                                      coordY)
                                            while shot_success:
                                                board_stand = proxy.get_obfuscated_boards(server_name, nickname, opponent_choice)
                                                if board_stand:
                                                    print(tabulate(board_stand))
                                                shot_success = proxy.validate_shot(server_name, nickname, opponent_choice, coordX, coordY)
                                            # if proxy.player_lost(server_name, nickname, opponent_choice):
                                            #     print("You have destroyed %s" % str(opponent_choice))
                                            next = proxy.next_players_turn(server_name, nickname)
                                            if next:
                                                my_turn, connected, hit = proxy.poll_my_turn(server_name, nickname)
                                        else:
                                            sleep(3)
                                            my_turn, connected, hit = proxy.poll_my_turn(server_name, nickname)
                                            if hit:
                                                who, board = proxy.hit_by_who(server_name, nickname)
                                                print 'Your ship was hit by %s' % who
                                                print(tabulate(board))
            else:
                server_name = game_servers.keys()[int(game_choice) - 1]
                join_request = proxy.join_game_server(server_name, nickname)
                if join_request:
                    has_joined_game = server_name
                    print 'Successfully connected %s' % game_choice

                    boats = proxy.get_boats(server_name, nickname)
                    board_setup = None
                    while boats:
                        selected_boat = raw_input("Select boat type (" + str(boats.keys()) + "): ")

                        if selected_boat.isdigit() and int(selected_boat) < len(boats.keys()):
                            selected_boat = boats.keys()[int(selected_boat)]

                        orientation = raw_input("Select orientation (horizontal, vertical) or (h, v): ")

                        if orientation == "h":
                            orientation = "horizontal"
                        elif orientation == "v":
                            orientation = "vertical"

                        start_x = int(raw_input("Select starting X coordinate (1-10): "))
                        while start_x + boats[selected_boat] - 1 > 10 and orientation == "vertical":
                            print("Invalid X coordinate, try again")
                            start_x = int(raw_input("Select starting X coordinate (1-10): "))

                        start_y = int(raw_input("Select starting Y coordinate (1-10): "))
                        while start_y + boats[selected_boat] - 1 > 10 and orientation == "horizontal":
                            print("Invalid Y coordinate, try again")
                            start_y = int(raw_input("Select starting Y coordinate (1-10): "))

                        checks_out = False
                        while not checks_out:
                            checks_out = proxy.check_position(server_name, selected_boat, orientation, start_x, start_y)
                            if not checks_out:
                                print("Place already taken, try again")
                                start_x = int(raw_input("Select starting X coordinate (1-10): "))
                                start_y = int(raw_input("Select starting Y coordinate (1-10): "))

                        if board_setup:
                            board_setup = proxy.set_up_board(server_name, nickname, selected_boat, orientation, start_x,
                                                             start_y, board_setup)
                        else:
                            board_setup = proxy.set_up_board(server_name, nickname, selected_boat, orientation, start_x,
                                                             start_y)
                        print(tabulate(board_setup))
                        del boats[selected_boat]
                    print 'Waiting for game to start'
                    while True:
                        game_active = proxy.game_active(server_name)
                        if game_active:
                            print 'Game is really active'
                            game_started = proxy.poll_game_start(server_name)
                            while not game_started:
                                sleep(3)
                                game_started = proxy.poll_game_start(server_name)
                            print 'Game has started'
                            my_turn, connected, hit = proxy.poll_my_turn(server_name, nickname)
                            while connected:
                                while not my_turn:
                                    sleep(3)
                                    my_turn, connected, hit = proxy.poll_my_turn(server_name, nickname)
                                    if hit:
                                        who, board = proxy.hit_by_who(server_name, nickname)
                                        print 'Your ship was hit by %s' % who
                                        print(tabulate(board))
                                print 'My turn'
                                opponents = proxy.choose_opponents(server_name, nickname)
                                print str(opponents)
                                opponent_choice = False
                                while not opponent_choice:
                                    opponent_choice = raw_input('Choose opponent (1-%d)' % len(opponents))
                                    opponent_choice = int(opponent_choice) - 1
                                    if opponent_choice > len(opponents) - 1 or opponent_choice < 0:
                                        print 'That is not an option.'
                                        opponent_choice = False
                                coordX = raw_input('Choose X coordinate: ')
                                coordY = raw_input('Choose Y coordinate: ')
                                coordX = int(coordX)
                                coordY = int(coordY)

                                shot_success = proxy.validate_shot(server_name, nickname, opponent_choice, coordX,
                                                                   coordY)
                                while shot_success:
                                    board_stand = proxy.get_obfuscated_boards(server_name, nickname, opponent_choice)
                                    if board_stand:
                                        print(tabulate(board_stand))
                                    shot_success = proxy.validate_shot(server_name, nickname, opponent_choice, coordX,
                                                                       coordY)
                                # if proxy.player_lost(server_name, nickname, opponent_choice):
                                #     print("You have destroyed %s" % str(opponent_choice))
                                next = proxy.next_players_turn(server_name, nickname)

                else:
                    print 'Game already has a player with that nickname!'
        except Exception as e:
            LOG.error('Error %s ' % str(e))

        if has_joined_game:
            proxy.disconnect_game_server(has_joined_game, nickname)
    else:
        print 'No servers active, sorry.'

    print 'Terminating ...'


if __name__ == '__main__':
    parser = ArgumentParser(description=__info(),
                            version=___VER)
    parser.add_argument('-H', '--host', \
                        help='Server INET address ' \
                             'defaults to %s' % DEFAULT_SERVER_INET_ADDR, \
                        default=DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p', '--port', type=int, \
                        help='Server TCP port, ' \
                             'defaults to %d' % DEFAULT_SERVER_PORT, \
                        default=DEFAULT_SERVER_PORT)
    args = parser.parse_args()
    mboard_client_main(args)
