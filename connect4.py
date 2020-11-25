import numpy as np
import argparse
import random

from node import *
from flags import *

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.currentNode = Node(np.full((self.height, self.width), MARK_EMPTY)) 
        self.winner = MARK_EMPTY

        self.history = []


    """
        Board.getValidMoves():
            returns a list of columns that can still have chips placed in them
    """
    def getValidMoves(self):
        return self.currentNode.getValidMoves()

    """
        Board.performMove()
            Simulate a drop of a piece into the board
    """
    def performMove(self, col, mark):
        #self.currentNode = Node(np.copy(self.currentNode.board), self.history, [(col, mark)])
        self.currentNode.simulateMove(col, mark)

        #self.history.append((col, mark))

        if self.currentNode.checkWin(mark) >= 4:
            self.winner = mark
    
    def negaMax(self, node, depth, playerToMove):
        #print("negamax() depth={}, player={}".format(depth, playerToMove))
        #node.print()
        validCols = node.getValidMoves()
        nodeScore = self.currentNode.evalPosition(playerToMove)
        #print("nodeScore for",playerToMove,"=",nodeScore)
        if len(validCols) == 0:
            if nodeScore < 4: # tie
                return 0
            else:   # win on last move
                return nodeScore
        
        if depth == maxDepth: 
            return nodeScore

        bestscore = -50

        for col in validCols: # simulate opponent responses
            newPlayer = int(not playerToMove-1) + 1 #ewww grosss... but it works :)
            node.simulateMove(col, newPlayer)
            score = self.negaMax(node, depth+1, newPlayer)
            
            bestscore = max(bestscore, -score)

            node.undoLastMove()

        return bestscore

    """
        Board.print():
             simply formats and prints the board to the screen
    """
    def print(self):
        self.currentNode.print()


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
        validCols = self.boardRef.getValidMoves()
        scores = []
        for col in validCols:
            #print("\n\n\n\nBegin Negamax for column",col)
            self.boardRef.currentNode.simulateMove(col, self.mark)
            scores.append(self.boardRef.negaMax(self.boardRef.currentNode, 1, self.mark))
            #print("Column {} score: {}".format(col, scores[-1]))
            self.boardRef.currentNode.undoLastMove()
        
        bestScore = max(scores)
        choice = validCols[scores.index(bestScore)]
        print(validCols)
        print(scores)
        print("Computer player chose column", choice)
        self.boardRef.performMove(choice, self.mark)

def waitForInput():
    if doSteps:
        input("Press Enter to continue")



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
                print("Player 1's Turn:")
            
            elif i == 1:
                print("Player 2's Turn:")

            print("Current Board:\n")
            board.print()
            players[i].makeMove()
            if board.winner != MARK_EMPTY:
                break
            
            waitForInput()

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
parser.add_argument("-test", type=int, default=1, help="Define number of tests to simulate")
parser.add_argument("-difficulty", type=int, default=2, help="Set Minimax search depth.")
parser.add_argument("-p1", choices=["human", "random", "computer"], default="human", help="Define player 1 type")
parser.add_argument("-p2", choices=["human", "random", "computer"], default="human", help="define player 2 type")
parser.add_argument("-step", action="store_true", help="Single Step through turns")
parser.add_argument("width", type=int, nargs='?', default=7)
parser.add_argument("height", type=int, nargs='?', default=6)

commandLineArgs = vars(parser.parse_args())
numTests = commandLineArgs["test"]  # Will be used to evaluate performance later
maxDepth = commandLineArgs["difficulty"]

p1Type = commandLineArgs["p1"]
p2Type = commandLineArgs["p2"]
doSteps = commandLineArgs["step"]

for i in range(numTests): # if numTests unspecified with arguments, default to 1 and play one game
    playOneGame(p1Type, p2Type)


