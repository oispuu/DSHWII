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
    def __init__(self,x,y):
        self.boats = {
            "destroyer[2]": 2,
            "submarine[3]": 3,
            "cruiser[3]": 3,
            "battleship[4]": 4,
            "carrier[5]": 5
        }
        self.board = [[0 for row in range(int(x)+2)] for column in range(int(y))]
        self.players = {}
        self.opponents = {}
        self.notifications = {}
        for row in self.board:
            row[0] = "|"
            row[int(x)+1] = "|"
        self.x = x
        self.y = y

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
                board[start_x - 1][start_y] = 1
                start_y += 1
                counter += 1
        if orientation.lower() == "vertical":
            while counter < size:
                board[start_x - 1][start_y] = 1
                start_x += 1
                counter += 1
        del boats[boat_type]
        self.players[nick_name] = board
        return board

    def get_player_board(self, opponent_name, nick_name):
        return self.players[opponent_name]

    def update_player_board(self, me, nick_name, new_board):
        if not me in self.opponents:
            self.opponents[me] = [{nick_name: new_board}]
            return True
        else:
            for opponent in range(0, len(self.opponents[me])):
                if self.opponents[me][opponent] == nick_name:
                    self.opponents[me][opponent] = new_board
                    return True
            self.opponents[me].append({nick_name: new_board})
            return True

    def has_been_hit(self, hitter, hittee, board):
        if board:
            self.players[hittee] = copy.deepcopy(board)
            self.notifications[hittee] = hitter
        else:
            self.notifications[hittee] = hitter
        return True


class MessageBoard():
    def __init__(self):
        self.__m_board = {}  # For storing published messages
        self.__m_uuid = 0  # For generating unique iDs
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

    def create_game_server(self, server_name, player, board_width, board_height):
        # Stupid logic, I have 1 dict for players and another one to identify the game object.
        self.available_game_servers[server_name] = [player]
        self.games_initialized[server_name] = Game(board_width,board_height)
        print 'Created a game server %s for player %s' % (server_name, player)
        return True

    def get_boats(self, server_name, player):
        return self.games_initialized[server_name].boats.copy()

    def check_position(self, server_name, player, boat_type, orientation, start_x, start_y):
        boats = self.games_initialized[server_name].boats.copy()
        board = None
        if player in self.games_initialized[server_name].players.keys():
            board = copy.deepcopy(self.games_initialized[server_name].players[player])
        else:
            board = copy.deepcopy(self.games_initialized[server_name].board)
        for i in range(0, boats[boat_type]):
            if orientation == "horizontal" and board[start_x - 1][start_y + i] == 1:
                return False
            if orientation == "vertical" and board[start_x + i - 1][start_y] == 1:
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
            for num_list in range(0, len(self.games_initialized[server_name].players[player])):
                checksum += sum([int(x) for x in filter(lambda y: isinstance(y, int) and int(y) == 1,
                                                        self.games_initialized[server_name].players[player][num_list])])

        if checksum == len(self.available_game_servers[server_name]) * 17:
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
        return self.active_games[server_name] == nickname, nickname in self.available_game_servers[server_name], nickname in self.games_initialized[server_name].notifications.keys()

    def choose_opponents(self, server_name, nickname):
        opponents = copy.deepcopy(self.available_game_servers[server_name])
        opponents.remove(nickname)
        return opponents

    def validate_shot(self, me, server_name, nickname, coordX, coordY):
        board = self.games_initialized[server_name].players[nickname]
        print 'Got board!'
        if board[coordX - 1][coordY] == 1:
            print 'Was hit!'
            board[coordX - 1][coordY] = "X"
            self.games_initialized[server_name].update_player_board(me, nickname, copy.deepcopy(board))
            self.games_initialized[server_name].has_been_hit(me, nickname, copy.deepcopy(board))
            return True
        else:
            print 'Miss!'
            board[coordX - 1][coordY] = "M"
            self.games_initialized[server_name].update_player_board(me, nickname, copy.deepcopy(board))
            self.games_initialized[server_name].has_been_hit(me, nickname, copy.deepcopy(board))
            return False

    def get_obfuscated_boards(self, server_name, me, opponent):
        available_boards = self.games_initialized[server_name].opponents[me]
        for index in range(0, len(available_boards)):
            key = available_boards[index].keys()[0]
            if key == opponent:
                for row in range(0, len(available_boards[index][key])):
                    available_boards[index][key][row] = [0 if x==1 else x for x in available_boards[index][key][row]]
                return available_boards[index][key]
        return False

    def player_lost(self, server_name, nickname):
        checksum = 0
        board = self.games_initialized[server_name].get_player_board(nickname)
        for i in range(0, len(board)):
            for j in range(0, len(board[i])):
                if board[i][j] == "X":
                    checksum += 1
        if checksum == 17:
            for player in self.available_game_servers[server_name]:
                if player == nickname:
                    self.available_game_servers[server_name].remove(nickname)
        return checksum == 17

    def game_active(self, server_name):
        return True if self.games_initialized[server_name] else False

    def get_board_size(self, server_name):
        return self.games_initialized[server_name].x, self.games_initialized[server_name].y

    def get_board(self, server_name, player):
        if self.games_initialized[server_name].players[player]:
            return self.games_initialized[server_name].players[player]
        else:
            return 1

    def hit_by_who(self, server_name, player):
        who = self.games_initialized[server_name].notifications[player]
        board = self.games_initialized[server_name].players[player]

        del self.games_initialized[server_name].notifications[player]

        return who, board

    def next_player(self, server_name, nickname):
        for i in range(0, len(self.available_game_servers[server_name])):
            if nickname == self.available_game_servers[server_name][i]:
                print 'Next player up, %s' % self.available_game_servers[server_name][i]
                if i+1 < len(self.available_game_servers[server_name]):
                    self.active_games[server_name] = self.available_game_servers[server_name][i+1]
                else:
                    self.active_games[server_name] = self.active_games[server_name][0]
        return True

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
        server.shutdown()  # Stop the serve-forever loop
        server.server_close()  # Close the sockets
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
    mboard_server_main(args)
