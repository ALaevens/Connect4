def maxAdjacent(ls):
    pScore = 0
    oScore = 0

    runningTotalP = 0
    runningTotalO = 0
    for piece in ls:
        if piece == 1:
            oScore = max(oScore, runningTotalO)
            runningTotalO = 0

            runningTotalP +=1
        
        elif piece != 0:
            pScore = max(pScore, runningTotalP)
            runningTotalP = 0

            runningTotalO +=1
    
    pScore = max(pScore, runningTotalP)
    oScore = max(oScore, runningTotalO)

    return pScore, oScore


print(maxAdjacent([2,0,1,2]))