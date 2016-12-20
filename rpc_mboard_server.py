'''
Created on Oct 27, 2016

@author: devel
'''

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from time import time
from xmlrpclib import ServerProxy
from argparse import ArgumentParser
import copy
import tabulate

___NAME = 'MBoard Client'
___VER = '0.2.0.0'
___DESC = 'Simple Message Board Client (RPC version)'
___BUILT = '2016-10-27'
___VENDOR = 'Copyright (c) 2016 DSLab'

DEFAULT_SERVER_PORT = 7778
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'

def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)


class Game:
    def __init__(self):
        self.boats = {
            "destroyer[2]": 2,
            "submarine[3]": 3,
            "cruiser[3]": 3,
            "battleship[4]": 4,
            "carrier[5]": 5
        }
        self.board = [[0 for row in range(12)] for column in range(10)]
        self.players = {}
        for row in self.board:
            row[0] = "|"
            row[11] = "|"

    # def setUpBoard(self, nick_name, boats, board):
        # boatType = raw_input("Select boat type (" + str(boats.keys()) + "): ")
        # orientation = raw_input("Select orientation (horizontal, vertical): ")
        #
        # startX = int(raw_input("Select starting X coordinate (1-10): "))
        # while startX + boats[boatType] - 1 > 10 and orientation == "vertical":
        #     print("Invalid X coordinate, try again")
        #     startX = int(raw_input("Select starting X coordinate (1-10): "))
        #
        # startY = int(raw_input("Select starting Y coordinate (1-10): "))
        # while startY + boats[boatType] - 1 > 10 and orientation == "horizontal":
        #     print("Invalid Y coordinate, try again")
        #     startY = int(raw_input("Select starting Y coordinate (1-10): "))
        #
        # # check if the place is still free
        # for i in range(0,boats[boatType]):
        #     while orientation == "horizontal" and board[startX - 1][startY + i] == 1:
        #         print("Place already taken, try again")
        #         startX = int(raw_input("Select starting X coordinate (1-10): "))
        #         startY = int(raw_input("Select starting Y coordinate (1-10): "))
        #     while orientation == "vertical" and board[startX + i - 1][startY] == 1:
        #         print("Place already taken, try again")
        #         startX = int(raw_input("Select starting X coordinate (1-10): "))
        #         startY = int(raw_input("Select starting Y coordinate (1-10): "))

    def set_up_board(self, nick_name, boat_type, orientation, start_x, start_y, board=None):
        boats = self.boats.copy()
        if not board:
            board = copy.deepcopy(self.board)
        else:
            board = self.players[nick_name]
        size = boats[boat_type]
        counter = 0
        if orientation.lower() == "horizontal":
            while counter < size:
                board[start_x-1][start_y] = 1
                start_y += 1
                counter += 1
        if orientation.lower() == "vertical":
            while counter < size:
                board[start_x-1][start_y] = 1
                start_x += 1
                counter += 1
        del boats[boat_type]
        self.players[nick_name] = board
        return board

    def get_player_board(self, nick_name):
        return self.players[nick_name]

    def update_player_board(self, nick_name, new_board):
        self.players[nick_name] = new_board

class MessageBoard():

    def __init__(self):
        self.__m_board = {} # For storing published messages
        self.__m_uuid = 0   # For generating unique iDs
        # Holds the players
        self.available_game_servers = {}
        # Holds the game object
        self.games_initialized = {}
        self.active_games = {}

    def __get_uuid(self):
        uuid = self.__m_uuid
        self.__m_uuid += 1
        return uuid

    def get_game_servers(self):
        return self.available_game_servers

    def get_players_in_session(self, server_name):
        return self.available_game_servers[server_name]

    def create_game_server(self, server_name, player):
        # Stupid logic, I have 1 dict for players and another one to identify the game object.
        self.available_game_servers[server_name] = [player]
        self.games_initialized[server_name] = Game()
        print 'Created a game server %s for player %s' % (server_name, player)
        return True

    def get_boats(self, server_name, player):
        return self.games_initialized[server_name].boats.copy()

    def check_position(self, server_name, boat_type, orientation, start_x, start_y):
        boats = self.games_initialized[server_name].boats.copy()
        board = copy.deepcopy(self.games_initialized[server_name].board)
        for i in range(0,boats[boat_type]):
            while orientation == "horizontal" and board[start_x - 1][start_y + i] == 1:
                return False
            while orientation == "vertical" and board[start_x + i - 1][start_y] == 1:
                return False
        return True

    def set_up_board(self, server_name, player, boat_type, orientation, start_x, start_y, board=None):
        return self.games_initialized[server_name].set_up_board(player, boat_type, orientation, start_x, start_y, board)

    def join_game_server(self, server_name, player):
        if player in self.available_game_servers[server_name]:
            return False
        else:
            self.available_game_servers[server_name].append(player)
            return True

    def disconnect_game_server(self, server_name, player):
        if player in self.available_game_servers[server_name]:
            self.available_game_servers[server_name].remove(player)
        if not self.available_game_servers[server_name]:
            del self.available_game_servers[server_name]

    def start_game(self, server_name, nickname):
        checksum = 0
        for player in self.games_initialized[server_name].players.keys():
            for num_list in range(0,len(self.games_initialized[server_name].players[player])):
                checksum += sum([int(x) for x in filter(lambda y: isinstance(y, int) and int(y) == 1, self.games_initialized[server_name].players[player][num_list])])

        if checksum == len(self.available_game_servers[server_name])*17:
            if nickname == self.available_game_servers[server_name][0]:
                self.active_games[server_name] = self.available_game_servers[server_name][0]
                return True
            else:
                print "Error starting game!!"
                return False
        else:
            return False

    def poll_game_start(self, server_name):
        return True if server_name in self.active_games.keys() else False

    def poll_my_turn(self, server_name, nickname):
        return self.active_games[server_name] == nickname, nickname in self.available_game_servers[server_name]

    def choose_opponents(self, server_name, nickname):
        opponents = copy.deepcopy(self.available_game_servers[server_name])
        return opponents.remove(nickname)

    def validate_shot(self, server_name, nickname, coordX, coordY):
        board = self.games_initialized[server_name].get_player_board(nickname)
        if board[coordX-1][coordY] == 1:
            board[coordX-1][coordY] = "X"
            self.games_initialized[server_name].update_player_board(nickname, copy.deepcopy(board))
            print("Hit it!")
        print("Missed it")
        for i in range(0,len(board)):
            for j in range(0,len(board[i])):
                if board[i][j] == 1:
                    board[i][j] = 0
        return board

    def game_active(self, server_name):
        return True if self.games_initialized[server_name] else False


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