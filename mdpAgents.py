# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

# This class, Grid, is not created by me and has been copied from the class mapAgents.py
# This code has been given to me by Frederik Mallmann-Trenn for my coursework.
# The creator and source for this code can be found in the comments at the top of this file
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

# This class consists of code copied and edited from the class mapAgents.py 
# This can be found in the comments at the top of this file
# It has been edited to make pacman move by itself using and MDP plaenr
class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.makeMap(state)
        self.addWallsToMap(state)
        self.updateFoodInMap(state)
        self.map.display()
        self.map.setValue(api.whereAmI(state)[0], api.whereAmI(state)[1], 1)
        self.chooseGridVar()
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
    
        # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        self.values = Grid(width,height)
        self.oldMap = Grid(width,height)
        self.ghostMap = Grid(width,height)
        self.oldGhostMap = Grid(width,height)

    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, 0)
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], 5)    
        for i in range(len(api.capsules(state))):
            self.map.setValue(api.capsules(state)[i][0], api.capsules(state)[i][1], 7)
    
    # Sets the parameters for the MDP agent based on map size
    def chooseGridVar(self):
        if self.map.width <=8:
            self.iterations = 20
            self.foodRew = 1
            self.ghostVal = 2
            self.moveRew = -0.08
            self.gamma = 0.8
            self.ghostMapMoveRew = -0.25
            self.ghostMapGamma = 0.7
        else:
            self.iterations = 25
            self.foodRew = 1
            self.ghostVal = 6
            self.moveRew = -0.08
            self.gamma = 0.8
            self.ghostMapMoveRew = -0.25
            self.ghostMapGamma = 0.7

    
    def getAction(self, state):
        self.updateFoodInMap(state)
        
        walls = api.walls(state)
        food = api.food(state)
        ghosts = api.ghosts(state)      

        # copies all values in main map to map used for val iteration intially
        for i in range(self.values.getWidth()):     
                for j in range(self.values.getHeight()):
                    if (i,j) in walls:
                        self.values.setValue(i,j, '%')
                    else:
                        self.values.setValue(i,j, self.map.getValue(i,j))

        # copies values in ghost map to be used to calculate ghost map utilities initially
        for i in range(self.values.getWidth()):     
            for j in range(self.values.getHeight()): 
                if (i,j) in walls:
                    self.ghostMap.setValue(i,j, '%')
                elif (i,j) in ghosts:
                    self.ghostMap.setValue(i,j, self.ghostVal)  
                else:
                    self.ghostMap.setValue(i,j, 0)
        
        for cnt in range(self.iterations):       
            # This copies the values in the main value iteration map into a second map 
            for i in range(self.oldMap.getWidth()):
                for j in range(self.oldMap.getHeight()): 
                    self.oldMap.setValue(i,j, self.values.getValue(i,j))

            # copies values from main ghost map to a second copy map
            for i in range(self.oldGhostMap.getWidth()):
                for j in range(self.oldGhostMap.getHeight()): 
                    self.oldGhostMap.setValue(i,j, self.ghostMap.getValue(i,j))

            # iterates over every position in map
            for i in range(self.map.getWidth()):
                for j in range(self.map.getHeight()):                    
                    if (i,j) in walls :#or (i,j) in food:
                        continue

                    north = (i,j+1)
                    east = (i+1,j)
                    south = (i,j-1)
                    west = (i-1,j)
                    direc = [north,east,south,west]
                    # This checks all directions and makes them equal to the 
                    # current position if that direction is a wall
                    n = 0                    
                    for x in direc:
                        if (x[0], x[1]) in walls:
                            direc[n] = (i,j)
                        n +=1
                    
                    # This block calculates the utilities for each possible move 
                    # for a position in the map containing only food 
                    norVal = self.oldMap.getValue(direc[0][0], direc[0][1])
                    eastVal = self.oldMap.getValue(direc[1][0], direc[1][1])
                    sthVal = self.oldMap.getValue(direc[2][0], direc[2][1])
                    westVal = self.oldMap.getValue(direc[3][0], direc[3][1])
                    up = 0.8*norVal + 0.1*eastVal + 0.1*westVal
                    right = 0.8*eastVal + 0.1*sthVal + 0.1*norVal
                    down = 0.8*sthVal + 0.1*westVal + 0.1*eastVal
                    left = 0.8*westVal + 0.1*norVal + 0.1*sthVal

                    # Here the utility for each position is calculated based on a map 
                    # which only contains ghosts
                    run = 0
                    if (i,j) not in ghosts:
                        norVal = self.oldGhostMap.getValue(direc[0][0], direc[0][1])
                        eastVal = self.oldGhostMap.getValue(direc[1][0], direc[1][1])
                        sthVal = self.oldGhostMap.getValue(direc[2][0], direc[2][1])
                        westVal = self.oldGhostMap.getValue(direc[3][0], direc[3][1])
                        ghostMapUp = 0.8*norVal + 0.1*eastVal + 0.1*westVal
                        ghostMapRight = 0.8*eastVal + 0.1*sthVal + 0.1*norVal
                        ghostMapDown = 0.8*sthVal + 0.1*westVal + 0.1*eastVal
                        ghostMapLeft = 0.8*westVal + 0.1*norVal + 0.1*sthVal                        
                        run = round(self.ghostMapMoveRew + self.ghostMapGamma*max(ghostMapUp,ghostMapRight,ghostMapDown,ghostMapLeft), 3)
                    else:
                        run = self.ghostMap.getValue(i,j)
                    self.ghostMap.setValue(i,j, run)

                    REW = 0
                    if (i,j) in food:
                        REW = self.foodRew    
                    else:
                        REW = self.moveRew     
                    # The rewards from the map with food is subtracted by the
                    # corresponding value in the utility map which only contains ghosts
                    REW -= run

                    val = round(REW + self.gamma * max(up,right,down,left), 3)
                    self.values.setValue(i,j, val)

            # uncomment this to see utilities which pacman uses which are calculated every iteration
            # print 'VALUESSSSSSSSSS: '
            # self.values.prettyDisplay()

            # uncomment to see the utility map of the ghosts every iteration
            # print 'SPOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOKY: '
            # self.ghostMap.prettyDisplay()
            
        # uncomment to see final utility map used by pacman every move
        # print 'VALUESSSSSSSSSS: '
        # self.values.prettyDisplay()
        
        # Removes STOP from the moves pacman can make
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # This section calculates the move with the maximum expected utility for pacman
        allExpUtil = []
        for direction in legal:
            curpos = api.whereAmI(state)
            expect = 0
            if direction == Directions.NORTH:
                direc = [(0,1), (1,0), (-1,0)]  # north, east, west
                n=0
                for x in direc:
                    if self.values.getValue(curpos[0] + direc[n][0], curpos[1]+direc[n][1]) == '%':
                        direc[n] =(0,0)
                    n+=1
                
                north = 0.8* self.values.getValue(curpos[0], curpos[1]+ direc[0][1])
                east = 0.1* self.values.getValue(curpos[0]+ direc[1][0], curpos[1]) 
                west = 0.1* self.values.getValue(curpos[0] + direc[2][0], curpos[1])
                expect = north+east+west
                allExpUtil = allExpUtil + [(expect, Directions.NORTH)]
                
                # curpos[0] #x
                # curpos[1] #y
            if direction == Directions.EAST:
                direc = [(1,0), (0,1), (0,-1)]  # east,north,south
                n=0
                for x in direc:
                    if self.values.getValue(curpos[0] + direc[n][0], curpos[1]+direc[n][1]) == '%':
                        direc[n] =(0,0)
                    n+=1
                    
                east = 0.8* self.values.getValue(curpos[0]+ direc[0][0], curpos[1])
                north = 0.1*self.values.getValue(curpos[0], curpos[1]+ direc[1][1])
                south = 0.1*self.values.getValue(curpos[0], curpos[1]+ direc[2][1])
                expect = east+north+south
                allExpUtil = allExpUtil + [(expect, Directions.EAST)]


            if direction == Directions.SOUTH:
                direc = [(0,-1), (-1,0), (1,0)]  # south, west, east
                n=0
                for x in direc:
                    if self.values.getValue(curpos[0] + direc[n][0], curpos[1]+direc[n][1]) == '%':
                        direc[n] =(0,0)
                    n+=1

                south = 0.8*self.values.getValue(curpos[0], curpos[1]+ direc[0][1])
                west = 0.1* self.values.getValue(curpos[0] + direc[1][0], curpos[1])
                east = 0.1* self.values.getValue(curpos[0]+ direc[2][0], curpos[1])
                expect = south+west+east
                allExpUtil = allExpUtil + [(expect, Directions.SOUTH)]


            
            if direction == Directions.WEST:
                direc = [(-1,0), (0,1), (0,-1)]  # west,north,south
                n=0
                for x in direc:
                    if self.values.getValue(curpos[0] + direc[n][0], curpos[1]+direc[n][1]) == '%':
                        direc[n] =(0,0)
                    n+=1
                
                west = 0.8*self.values.getValue(curpos[0] + direc[0][0], curpos[1])
                north = 0.1*self.values.getValue(curpos[0], curpos[1]+ direc[1][1])
                south = 0.1*self.values.getValue(curpos[0], curpos[1]+ direc[2][1])
                expect = west+north+south
                allExpUtil = allExpUtil + [(expect, Directions.WEST)]
        
        bestVal = allExpUtil[0][0]
        bestDir = [allExpUtil[0][1]]
        
        for x in range(0, len(allExpUtil)):     # check for direction with highest utility
            if allExpUtil[x][0] > bestVal:
                bestVal = allExpUtil[x][0]
                bestDir = [allExpUtil[x][1]]

        for x in range(0, len(allExpUtil)):         # add any other directions which have the same utility
            if allExpUtil[x][0] == bestVal and allExpUtil[x][1] != bestDir[0][1]:
                bestDir.append(allExpUtil[x][1])

        bestDir = list(set(bestDir))
        
        return api.makeMove(random.choice(bestDir), legal)

