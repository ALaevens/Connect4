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
    
    """
        Node.getValidMoves():
            Get the valid moves from a node.
    """
    def getValidMoves(self):
        validCols = []
        for col in range(self.width):  # loop along top row
            if self.board[0][col] == MARK_EMPTY:
                validCols.append(col)  # mark empty spaces as valid
        return validCols

    """
        Node.inBounds():
            Check if a given row, col position is within the bounds of the board
    """
    def inBounds(self, row, col):
        if row < 0 or row >= self.height:
            return False

        if col < 0 or col >= self.width:
            return False

        return True
    
    """
        Node.simulateMove()
            Simulate a drop of a piece into the board
            
            Parameters:
                col: column to drop piece in
                marK: player piece to mark board with
            
            Return:
                row, col position of where the piece landed
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
    
    """
        Node.undoLastMove():
            Undo the last move made in the game.
    """
    def undoLastMove(self):
        if len(self.placementHistory) > 0:
            lastPos = self.placementHistory.pop()
            self.board[lastPos[0]][lastPos[1]] = MARK_EMPTY
            


    """
        Node.checkWin():
            Called by Node.SimulateMove() when placing a piece. Only need to check the surrounding area of the
            placed piece because that is the only move that could have possible contributed to a winning move
            
            Parameters:
                Move: To check most recent takes in None, or can take a specific location to check for wins
                
            Return:
            boolean,mark of the player checked
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
    
    """
        Node.fullWinCheck():
            Performs a win check on every piece on the board

            Return:
            Boolean, None or winner
    """
    def fullWinCheck(self):
        for move in self.placementHistory[::-1]:
            won, winner = self.checkWin(move)
            if won:
                return True, winner

        return False, None

    """
        Node.evalPosition():
            Evaluates the heuristic values of a turn for the given player.

            Parameters:
                player: the heuristic will be calculated for this player
    """
    def evalPosition(self, player):
        def maxAdjacent(ls): # [UNUSED] find the maximum number of adjacent player and opponent pieces in a line
            pScore = 0
            oScore = 0

            if len(ls) < 4: # ignore lines of length less than 4
                return 0, 0

            runningTotalP = 0
            runningTotalO = 0
            for piece in ls:
                if piece == player:
                    # player piece encountered, reset opponent counter
                    oScore = max(oScore, runningTotalO)
                    runningTotalO = 0
                    
                    # increment player counter
                    runningTotalP +=1
                
                elif piece != MARK_EMPTY:
                    # opponent piece encountered, reset player counter
                    pScore = max(pScore, runningTotalP)
                    runningTotalP = 0

                    # increment opponent counter
                    runningTotalO +=1
            
            pScore = max(pScore, runningTotalP)
            oScore = max(oScore, runningTotalO)

            return pScore, oScore
                
        def adjToScore(n): # [UNUSED] apply arbitrarily selected heuristic values to number of adjacent pieces
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
        

        def lineScore(ls): # scoring heuristic based on youtube video
            score = 0
            if len(ls) < 4:
                return 0
            
            for i in range(0, len(ls)-3):
                lineSeg = ls[i:i+4]
                playerCount = np.count_nonzero(lineSeg == player)
                emptyCount = np.count_nonzero(lineSeg == MARK_EMPTY)
                opponentCount = 4 - (playerCount + emptyCount)

                if playerCount == 4:
                    score += 100
                
                if playerCount == 3 and emptyCount == 1:
                    score += 10
                
                if playerCount == 2 and emptyCount == 2:
                    score += 5
                
                if opponentCount == 3 and emptyCount == 1:
                    score -= 80
            
            return score

        height = self.height
        width = self.width
        score = 0
        
        # horizontal dont need to check 3 from edge since you couldnt make 4 then
        for row in range(height):
            #pScore = maxAdjacent(self.board[row])[1]
            #score += adjToScore(pScore)  
            score += lineScore(self.board[row])
             

        # verticalCheck
        for col in range(width):
            #pScore = maxAdjacent(self.board[:, col])[1]
            #score += adjToScore(pScore)
            score += lineScore(self.board[:, col])

        # ascending diagonals        
        flippedBoard = np.fliplr(self.board)
        for i in range(-(height-1),width):
            #pScore = maxAdjacent(flippedBoard.diagonal(i))[1]
            #score += adjToScore(pScore)
            score += lineScore(flippedBoard.diagonal(i))

        # Descending diagonals
        for i in range(-(height-1),width):
            #pScore = maxAdjacent(self.board.diagonal(i))[1]
            #score += adjToScore(pScore)
            score += lineScore(self.board.diagonal(i))
            
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
