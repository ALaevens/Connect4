import numpy as np
from flags import *

class Node:
    def __init__(self, arr, moves = [], newMoves = []):
        self.board = arr
        self.moves = moves + newMoves
        self.newMoves = newMoves

        self.height, self.width = self.board.shape

        self.placementHistory = []
        for move in newMoves:
            self.simulateMove(move[0], move[1])
        
    def getValidMoves(self):
        validCols = []
        for col in range(self.width):  # loop along top row
            if self.board[0][col] == MARK_EMPTY:
                validCols.append(col)  # mark empty spaces as valid
        return validCols

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
        Board.performMove()
            Simulate a drop of a piece into the board
    """
    def simulateMove(self, col, mark):
        endRow = None
        for row in range(self.height):
            # if either conditions are true, the piece can fall no further
            if row == self.height-1 or self.board[row+1][col] != MARK_EMPTY:
                self.board[row][col] = mark  # place piece
                endRow = row
                break
        
        self.placementHistory.append((endRow, col, mark))
        return endRow, col
    

    def undoLastMove(self):
        if len(self.placementHistory) > 0:
            lastPos = self.placementHistory.pop()
            self.board[lastPos[0]][lastPos[1]] = MARK_EMPTY
            


    """
        Board.checkWin():
            Called by Board.performMove() when placing a piece. Only need to check the surrounding area of the
            placed piece because that is the only move that could have possible contributed to a winning move
    """
    def checkWin(self, move = None):
        continuations = [0, 0, 0, 0, 0, 0, 0, 0]  # 0 = NE, 1 = E, 2 = SE, 3 = S, 4 = SW, 5 = W, 6 = NW, 7 = N
        lines = [0, 0, 0, 0]  # 0: +'ve diagonal, 1: -'ve diagonal, 2: horizontal, 3: vertical

        increments = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]

        row = col = mark = 0
        if move is None:
            row, col, mark = self.placementHistory[-1]
        else:
            row, col, mark = move

        # get current player's mark
        mark = self.board[row][col]
        for direction in range(8):  # check all directions except up (cant possibly have a piece above a new piece)
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
        lines[3] = continuations[3] + continuations[7] + 1

        # if a line of length >=4 has been formed, the player has one
        return max(lines) >= 4, mark

        #if player == mark:
        #    return max(lines)
        #else:
        #    return -max(lines)
    
    def fullWinCheck(self):
        for move in self.placementHistory[::-1]:
            won, winner = self.checkWin(move)
            if won:
                return True, winner

        return False, None


    def evalPosition(self, player):
        def maxAdjacent(ls):
            pScore = 0
            oScore = 0

            if len(ls) < 4:
                return 0, 0

            runningTotalP = 0
            runningTotalO = 0
            for piece in ls:
                if piece == player:
                    oScore = max(oScore, runningTotalO)
                    runningTotalO = 0

                    runningTotalP +=1
                
                elif piece != MARK_EMPTY:
                    pScore = max(pScore, runningTotalP)
                    runningTotalP = 0

                    runningTotalO +=1
            
            pScore = max(pScore, runningTotalP)
            oScore = max(oScore, runningTotalO)

            return pScore, oScore
                
        def adjToScore(n):
            if n > 3:
                return 1000
            if n == 3:
                return 10
            if n == 2:
                return 5
            if n == 1:
                return 0
            if n < 1:
                return 0
            return n
                    

        height = self.height
        width = self.width
        score = 0
        
        #horizontal dont need to check 3 from edge since you couldnt make 4 then
        for row in range(height):
            pScore, oScore = maxAdjacent(self.board[row])
            score += adjToScore(pScore)  
            #score -= adjToScore(oScore)*2
            #score += windowScore(self.board[row])
              

        #verticalCheck
        for col in range(width):
            pScore, oScore = maxAdjacent(self.board[:, col])
            score += adjToScore(pScore)
            #score -= adjToScore(oScore)*2
            #score += windowScore(self.board[:, col])



        #ascendingDiag [0,1,2] flp horizontally
        #              [3,4,5]
        # i = 0 gives [3,1]
        # i = 1 gives [4,2]
        # https://stackoverflow.com/questions/6313308/get-all-the-diagonals-in-a-matrix-list-of-lists-in-python
        
        flippedBoard = np.fliplr(self.board)
        for i in range(-(height-1),width):
            pScore, oScore = maxAdjacent(flippedBoard.diagonal(i))
            score += adjToScore(pScore)
            #score -= adjToScore(oScore)*2
            #score += windowScore(flippedBoard.diagonal(i))


        #DescendingDiag [0,1,2]
        #               [3,4,5]
        # this also checks the corners is that bad?
        #i = 0 gives [0,4]
        #i = 1 gives [1,5]
        for i in range(-(height-1),width):
            pScore, oScore = maxAdjacent(self.board.diagonal(i))
            score += adjToScore(pScore)
            #score -= adjToScore(oScore)*2
            #score += windowScore(self.board.diagonal(i))

        #print(f"Total score: {score}")
        return score

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

        print("="*(self.width*2 + 1))
