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
    
    # https://stackoverflow.com/questions/5221236/python-my-classes-as-dict-keys-how
    def __eq__(self, another):
        return np.array_equal(self.board, another.board)
    
    def __hash__(self):
        return hash(self.board.tobytes())

    
    def getValidMoves(self):
        validCols = []
        for col in range(self.width):  # loop along top row
            if self.board[0][col] == MARK_EMPTY:
                validCols.append(col)  # mark empty spaces as valid
        return validCols

    def getChildren(self):
        nodes = []
        validCols = self.getValidMoves()

        nextPlayer = None
        if len(self.moves) % 2 == 0:
            nextPlayer = MARK_P1
        else:
            nextPlayer = MARK_P2

        for col in validCols:
            nodes.append(Node(np.copy(self.board), self.moves, [(col, nextPlayer)]))

        return nodes

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
    def checkWin(self, player):
        continuations = [0, 0, 0, 0, 0, 0, 0]  # 0 = NE, 1 = E, 2 = SE, 3 = S, 4 = SW, 5 = W, 6 = NW
        lines = [0, 0, 0, 0]  # 0: +'ve diagonal, 1: -'ve diagonal, 2: horizontal, 3: vertical

        increments = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

        row, col, mark = self.placementHistory[-1]

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
        if player == mark:
            return max(lines)
        else:
            return -max(lines)

    def evalPosition(self, player):
        def maxAdjacent(ls):
            pScore = 0
            oScore = 0

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

            #print(f"{ls}: pScore{pScore}, oScore:{oScore}")
            return pScore, oScore
        
        def adjToScore(n):          
            #return n*(n^3)
            return n
                    

        height = self.height
        width = self.width
        score = 0
        
        #horizontal dont need to check 3 from edge since you couldnt make 4 then
        for row in range(height):
            pScore, oScore = maxAdjacent(self.board[row])
            score += adjToScore(pScore)  
            score -= adjToScore(oScore)
              

        #verticalCheck
        for col in range(width):
            pScore, oScore = maxAdjacent(self.board[:, col])
            score += adjToScore(pScore)
            score -= adjToScore(oScore)



        #ascendingDiag [0,1,2] flp horizontally
        #              [3,4,5]
        # i = 0 gives [3,1]
        # i = 1 gives [4,2]
        # https://stackoverflow.com/questions/6313308/get-all-the-diagonals-in-a-matrix-list-of-lists-in-python
        
        flippedBoard = np.fliplr(self.board)
        for i in range(-(height-1),width):
            pScore, oScore = maxAdjacent(flippedBoard.diagonal(i))
            score += adjToScore(pScore)
            score -= adjToScore(oScore)


        #DescendingDiag [0,1,2]
        #               [3,4,5]
        #i = 0 gives [0,4]
        #i = 1 gives [1,5]
        for i in range(-(height-1),width):
            pScore, oScore = maxAdjacent(self.board.diagonal(i))
            score += adjToScore(pScore)
            score -= adjToScore(oScore)

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
