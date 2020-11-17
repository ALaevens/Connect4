import numpy as np
import argparse
import random

MARK_EMPTY = 0
MARK_P1 = 1
MARK_P2 = 2

WINCOND_TERMINATE = 3
WINCOND_TIE = 4


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = np.full((self.height, self.width), MARK_EMPTY)
        self.winner = MARK_EMPTY

    """
        Board.getValidMoves():
            returns a list of columns that can still have chips placed in them
    """
    def getValidMoves(self):
        validCols = []
        for col in range(self.width):  # loop along top row
            if self.board[0][col] == MARK_EMPTY:
                validCols.append(col)  # mark empty spaces as valid
        return validCols

    """
        Board.performMove()
            Simulate a drop of a piece into the board
    """
    def performMove(self, col, mark):
        for row in range(self.height):
            # if either conditions are true, the piece can fall no further
            if row == self.height-1 or self.board[row+1][col] != MARK_EMPTY:
                self.board[row][col] = mark  # place piece
                self.checkWin(row, col)  # Check if the move was a winning move
                return

    """
        Board.inBounds():
            Check if a given row, col position is within the bounds of the board
    """
    def inBounds(self, row, col):
        if row < 0 or row >= self.height:
            return False

        if col < 0 or col >= self.width:
            return False

        return True

    """
        Board.checkWin():
            Called by Board.performMove() when placing a piece. Only need to check the surrounding area of the
            placed piece because that is the only move that could have possible contributed to a winning move
    """
    def checkWin(self, row, col):
        continuations = [0, 0, 0, 0, 0, 0, 0]  # 0 = NE, 1 = E, 2 = SE, 3 = S, 4 = SW, 5 = W, 6 = NW
        lines = [0, 0, 0, 0]  # 0: +'ve diagonal, 1: -'ve diagonal, 2: horizontal, 3: vertical

        increments = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

        # get current player's mark
        mark = self.board[row][col]
        for direction in range(7):  # check all directions except up (cant possibly have a piece above a new piece)
            incRow, incCol = increments[direction]
            distance = 1

            checkRow = incRow*distance + row
            checkCol = incCol*distance + col
            # iteratively check farther pieces from the dropped piece, count line length as distance
            while self.inBounds(checkRow, checkCol) and self.board[checkRow][checkCol] == mark:
                distance += 1
                checkRow = incRow * distance + row
                checkCol = incCol * distance + col

            continuations[direction] = distance-1

        # form the 4 possible lines
        lines[0] = continuations[0] + continuations[4] + 1
        lines[1] = continuations[2] + continuations[6] + 1
        lines[2] = continuations[1] + continuations[5] + 1
        lines[3] = continuations[3] + 1

        # if a line of length >=4 has been formed, the player has one
        if max(lines) >= 4:
            self.winner = mark
            return True
        else:
            return False

    """
        Board.print():
             simply formats and prints the board to the screen
    """
    def print(self):
        print(" " + " ".join(str(i) for i in range(self.width)))

        for row in range(self.height):
            arrayStr = np.array2string(self.board[row], separator=" ")
            arrayStr = arrayStr.replace(str(MARK_P1), "o")
            arrayStr = arrayStr.replace(str(MARK_P2), "+")
            arrayStr = arrayStr.replace(str(MARK_EMPTY), " ")
            print("|"+arrayStr[1:-1]+"|")

        print("̅"*(self.width*2 + 1))


class Player:
    def __init__(self, mark, boardRef):
        self.mark = mark
        self.boardRef = boardRef

    def makeMove(self):
        pass


class HumanPlayer(Player):
    def makeMove(self):
        validChoices = self.boardRef.getValidMoves()
        print("Valid Choices:", ", ".join(str(col) for col in validChoices))
        colStr = input("Choose Column > ")

        try:
            col = int(colStr)
            self.boardRef.performMove(col, self.mark)

        except:
            self.boardRef.winner = WINCOND_TERMINATE


class RandomPlayer(Player):
    def makeMove(self):
        validChoices = self.boardRef.getValidMoves()
        col = validChoices[random.randint(0, len(validChoices)-1)]

        print("Random Player chose column:", col)
        self.boardRef.performMove(col, self.mark)


class ComputerPlayer(Player):
    def makeMove(self):
        pass


def playOneGame(p1Type, p2Type):
    typeMap = {"human": HumanPlayer, "random": RandomPlayer, "computer": ComputerPlayer}
    board = Board(commandLineArgs['width'], commandLineArgs['height'])
    players = [typeMap[p1Type](MARK_P1, board), typeMap[p2Type](MARK_P2, board)]

    # Main Game loop. Play until a win or some ending condition
    while board.winner == MARK_EMPTY:
        # Alternate players
        for i in range(2):
            print("_" * 30, "\n")
            if i == 0:
                print("Player 1's Turn:\n")
                board.print()
                players[i].makeMove()
                if board.winner != MARK_EMPTY:
                    break

            elif i == 1:
                print("Player 2's Turn:\n")
                board.print()
                players[i].makeMove()
                if board.winner != MARK_EMPTY:
                    break

    print("_" * 30, "\n\nFinal Board:")
    board.print()

    if board.winner == MARK_P1:
        print("Player 1 has won!")
        return MARK_P1
    elif board.winner == MARK_P2:
        print("Player 2 has won!")
        return MARK_P2
    elif board.winner == WINCOND_TIE:
        print("The game has tied")
        return None
    elif board.winner == WINCOND_TERMINATE:
        print("A player has cancelled the game")
        return None


# Receive commandline arguments
parser = argparse.ArgumentParser(description="Simulate connect 4 games")
parser.add_argument("-test", type=int, default=0, help="Define number of tests to simulate")
parser.add_argument("-p1", choices=["human", "random", "computer"], default="human", help="Define player 1 type")
parser.add_argument("-p2", choices=["human", "random", "computer"], default="human", help="define player 2 type")
parser.add_argument("width", type=int, nargs='?', default=7)
parser.add_argument("height", type=int, nargs='?', default=6)

commandLineArgs = vars(parser.parse_args())
numTests = commandLineArgs["test"]  # Will be used to evaluate performance later


playOneGame(commandLineArgs["p1"], commandLineArgs["p2"])