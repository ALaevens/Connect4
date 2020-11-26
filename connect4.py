import numpy as np
import argparse
import random

from node import *
from flags import *

def debugLog(*text):
    if doDebugLog:
        print(*text)

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

        win, winner = self.currentNode.checkWin()
        if win:
            self.winner = winner

    # negamax implementation based on https://www.youtube.com/watch?v=8392NJjj8s0&feature=youtu.be
    def negaMax(self, node, depth, player):
        validCols = node.getValidMoves()
        winner = node.fullWinCheck()[1]

        opponent = int(not player-1) + 1 #ewww grosss... but it works :)
        if depth == maxDepth or winner != None or len(validCols) == 0:
            if winner != None or len(validCols) == 0:
                if winner == player:
                    debugLog("\t"*depth, "Terminus Reached, Returning", np.inf)
                    return None, np.inf
                elif winner != player:
                    debugLog("\t"*depth, "Terminus Reached, Returning", -np.inf)
                    return None, -np.inf
                else:
                    debugLog("\t"*depth, "Terminus Reached, Returning", 0)
                    return None, 0
            else:
                eval = node.evalPosition(player)
                debugLog("\t"*depth, "Terminus Reached, Returning eval:", eval)
                return None, eval
        
        value = -np.inf
        column = random.choice(validCols)
        colScoreMap = {}
        for col in validCols:
            node.simulateMove(col, player)
            newScore = -self.negaMax(node, depth+1, opponent)[1]
            debugLog("\t"*depth,f"[P{player}] {col}: {newScore}")

            if newScore not in colScoreMap:
                colScoreMap[newScore] = [col]
            else:
                colScoreMap[newScore].append(col)
            
            node.undoLastMove()
            if newScore > value:
                debugLog("\t"*depth,f"Update previous value {value} to {newScore} for column {col}")
                value = newScore
                column = col
        
        
        if depth == 0:
            print(colScoreMap)
            maxVal = max(colScoreMap)
            pick = random.choice(colScoreMap[maxVal])
            return pick, maxVal
        else:
            return column, value
    
    def miniMax(self, node, depth, player, playerIsMax):
        validCols = node.getValidMoves()
        winner = node.fullWinCheck()[1]

        opponent = int(not player-1) + 1 #ewww grosss... but it works :)
        if depth == maxDepth or winner != None or len(validCols) == 0:
            if winner != None or len(validCols) == 0:
                if winner == player and playerIsMax:
                    return None, 1000000000000000
                elif winner == player and not playerIsMax:
                    return None, -100000000000000
                elif winner != player:
                    debugLog("????????? Winner was not player!?!?! Winner was:", winner)
                else:
                    return None, 0
            else:
                return None, node.evalPosition(player)
        
        if playerIsMax:
            value = -np.inf
            column = random.choice(validCols)
            for col in validCols:
                node.simulateMove(col, player)
                newScore = self.miniMax(node, depth+1, opponent, False)[1]
                debugLog("\t"*depth,f"[MAX P{player}] {col}: {newScore}")
                node.undoLastMove()
                if newScore > value:
                    debugLog("\t"*depth,f"Update previous value {value} to {newScore} for column {col}")
                    value = newScore
                    column = col
            return column, value 
        else:
            value = np.inf
            column = random.choice(validCols)
            for col in validCols:
                node.simulateMove(col, player)
                newScore = self.miniMax(node, depth+1, opponent, True)[1]
                debugLog("\t"*depth,f"[MIN P{player}] {col}: {newScore}")
                node.undoLastMove()
                if newScore < value:
                    debugLog("\t"*depth,f"Update previous value {value} to {newScore} for column {col}")
                    value = newScore
                    column = col
            return column, value
    

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
        bestCol, score = self.boardRef.negaMax(self.boardRef.currentNode, 0, self.mark)
        if score == np.inf:
            print("Too easy!")
        elif score == -np.inf:
            print("The end is in sight... :(")

        print("Computer player choses column",bestCol,"with score", score)
        self.boardRef.performMove(bestCol, self.mark)


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

            if len(board.getValidMoves()) == 0:
                board.winner = WINCOND_TIE
                print("Board is full without win.... TIE")
                break

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
        return WINCOND_TIE
    elif board.winner == WINCOND_TERMINATE:
        print("A player has cancelled the game")
        return WINCOND_TERMINATE


# Receive commandline arguments
parser = argparse.ArgumentParser(description="Simulate connect 4 games")
parser.add_argument("-test", type=int, default=1, help="Define number of tests to simulate")
parser.add_argument("-difficulty", type=int, default=4, help="Set Minimax search depth.")
parser.add_argument("-p1", choices=["human", "random", "computer"], default="human", help="Define player 1 type")
parser.add_argument("-p2", choices=["human", "random", "computer"], default="human", help="define player 2 type")
parser.add_argument("-step", action="store_true", help="Single Step through turns")
parser.add_argument("-debug", action="store_true", help="PRINT ALL THE THINGS")
parser.add_argument("width", type=int, nargs='?', default=7)
parser.add_argument("height", type=int, nargs='?', default=6)

commandLineArgs = vars(parser.parse_args())
numTests = commandLineArgs["test"]  # Will be used to evaluate performance later
maxDepth = commandLineArgs["difficulty"]

p1Type = commandLineArgs["p1"]
p2Type = commandLineArgs["p2"]
doSteps = commandLineArgs["step"]
doDebugLog = commandLineArgs["debug"]

wins = [0, 0, 0] #Ties, P1, P2
for i in range(numTests): # if numTests unspecified with arguments, default to 1 and play one game
    try:
        winner = playOneGame(p1Type, p2Type)
    except KeyboardInterrupt:
        winner = WINCOND_TERMINATE

    if winner in [MARK_P1, MARK_P2]:
        wins[winner] += 1
    elif winner == WINCOND_TIE:
        wins[0] += 1
    elif winner == WINCOND_TERMINATE:
        break
    
print("P1 Wins:",wins[1])
print("P2 Wins:",wins[2])
print("Ties:",wins[0])
