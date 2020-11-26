CMPUT355 Project #4
Fa20

**Group Name:**
The Procrastinators

**Members:**
    
    Alexander Laevens: alaevens@ualberta.ca, 1604086
    
    Ryan Bowler: bowler@ualberta.ca, 1494895
    
    Andrew Simon: asimon@ualberta.ca, 1497170
    

**About this project:**

This is our connect 4 terminal game. Its played using keyboard and within a terminal.
To run it, you need python3 and numpy installed.
To start the game, one must run through a terminal.

**Starting the game:**

	python3 connect4.py

Starts a two player connect 4 game, player 1 as human and player 2 as human.
This is so you could play against someone.

This program also has lots of optional command line arguments. You can use -h or -help to see these.

They are explained in there but I will explain them breifly.

    -test NUM	run NUM times

    -depth          Search depth of the program (select computer as one or two of the players)

    -p1,p2		{human,random,computer} select what player should be... Random is placement of pieces at random

    -step		Used to watch computer v random or computer v computer games easier.. allows stepping through the program

    -debug		Used by the programmers to see what the program is actually doing (Behind the scences)

example of playing vs a computer at depth 4:

	python3 connect4.py -p1 computer -p2 human -depth 4

**Playing the game:**

To play, just follow the information on the screen. 
Each column is marked, input the number of the column you wish to drop your piece in.






**Resources used:**

UofA 355 notes on negamax,minimax and alpha beta

	http://webdocs.cs.ualberta.ca/~hayward/355/jem/355.html
    
negamax implementation based on

	https://www.youtube.com/watch?v=8392NJjj8s0&feature=youtu.be
	https://en.wikipedia.org/wiki/Negamax
    
NumPy Documentation

	https://numpy.org/doc/

