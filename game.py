from tabulate import tabulate

boats = {
    "destroyer": 2,
    "submarine": 3,
    "cruiser": 3,
    "battleship": 4,
    "carrier": 5
}

class Player:
    def createPlayer(self, nickName):
        player = {}
        player[nickName] = [[0 for row in range(12)] for column in range(10)]
        for row in player[nickName]:
            row[0] = "|"
            row[11] = "|"
        return player

class Board:
    def addBoat(self,nickName):
        board = nickName.values()

        boatType = raw_input("Select boat type: " + str(boats.keys()) + " ")
        startX = int(raw_input("Select starting X coordinate (0-10): "))
        startY = int(raw_input("Select starting Y coordinate (0-10): "))
        orientation = raw_input("Select orientation (horizontal, vertical): ")

        # check if the place is still free
        for i in range(0,boats[boatType]):
            while orientation == "horizontal" and board[0][startX - 1][startY + i] == 1:
                print("Place already taken, try again")
                startX = int(raw_input("Select starting X coordinate (0-10): "))
                startY = int(raw_input("Select starting Y coordinate (0-10): "))
            while orientation == "vertical" and board[0][startX + i - 1][startY] == 1:
                print("Place already taken, try again")
                startX = int(raw_input("Select starting X coordinate (0-10): "))
                startY = int(raw_input("Select starting Y coordinate (0-10): "))


        size = boats[boatType]
        counter = 0
        if orientation.lower() == "horizontal":
            while counter < size:
                board[0][startX-1][startY] = 1
                startY += 1
                counter += 1
        if orientation.lower() == "vertical":
            while counter < size:
                board[0][startX-1][startY] = 1
                startX += 1
                counter += 1
        del boats[boatType]
        return board

def setUpGame():
    player = Player()
    nickName = raw_input("Enter your nickname: ")
    player = player.createPlayer(nickName)
    board = Board()
    while boats:
        print(tabulate(board.addBoat(player)[0]))

setUpGame()