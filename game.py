from tabulate import tabulate
import weakref

boats = {
    "destroyer": 2,
    "submarine": 3,
    "cruiser": 3,
    "battleship": 4,
    "carrier": 5
}

board = [[0 for row in range(12)] for column in range(10)]

for row in board:
    row[0] = "|"
    row[11] = "|"

class Player:
    players = []

    def __init__(self,name=None):
        self.__class__.players.append(weakref.proxy(self))
        self.name = name

class Game:

    def setUpBoard(self, nickName):

        boatType = raw_input("Select boat type: " + str(boats.keys()) + " ")
        orientation = raw_input("Select orientation (horizontal, vertical): ")

        startX = int(raw_input("Select starting X coordinate (1-10): "))
        while startX + boats[boatType] - 1 > 10 and orientation == "vertical":
            print("Invalid X coordinate, try again")
            startX = int(raw_input("Select starting X coordinate (1-10): "))

        startY = int(raw_input("Select starting Y coordinate (1-10): "))
        while startY + boats[boatType] - 1 > 10 and orientation == "horizontal":
            print("Invalid Y coordinate, try again")
            startY = int(raw_input("Select starting Y coordinate (1-10): "))

        # check if the place is still free
        for i in range(0,boats[boatType]):
            while orientation == "horizontal" and board[startX - 1][startY + i] == 1:
                print("Place already taken, try again")
                startX = int(raw_input("Select starting X coordinate (1-10): "))
                startY = int(raw_input("Select starting Y coordinate (1-10): "))
            while orientation == "vertical" and board[startX + i - 1][startY] == 1:
                print("Place already taken, try again")
                startX = int(raw_input("Select starting X coordinate (1-10): "))
                startY = int(raw_input("Select starting Y coordinate (1-10): "))

        size = boats[boatType]
        counter = 0
        if orientation.lower() == "horizontal":
            while counter < size:
                board[startX-1][startY] = 1
                startY += 1
                counter += 1
        if orientation.lower() == "vertical":
            while counter < size:
                board[startX-1][startY] = 1
                startX += 1
                counter += 1
        del boats[boatType]
        return {nickName: board}

    def getPlayerList(self):
        playerList = []
        for instance in Player.players:
            playerList.append(instance.name)
        return playerList

    def shootAndValidate(self, player, row, column):
        enemy = raw_input("Select enemy to shoot: " + str(self.getPlayerList()))
        row = raw_input("Row: ")
        column = raw_input("Column: ")
        player[enemy]

    def setUpGame(self, player):
        while boats:
            print(tabulate(self.setUpBoard(player.name)[player.name]))

# not needed just initiate from server
# game = Game()
#game.setUpGame()

# jaanus = Player("Jaanus")
# urmas = Player("Urmas")
# saarmas = Player("Saarmas")

# setUpGame(game,jaanus)
# print(game.getPlayerList())