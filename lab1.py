# Tyler Lapiana - tjl9096
# Lab 1

import sys
import math
from PIL import Image
from queue import PriorityQueue


# Main Function
# Interprets input and calls the functions that do most of the work
# Finally, saves the image at the end of the program
def main():
    imageFile = sys.argv[1]
    elevationsFile = sys.argv[2]
    path = sys.argv[3]
    output = sys.argv[4]

    terrain = getImage(imageFile)  # terrain.size[0] => x - .size[1] => y
    elevations = getElevation(elevationsFile)  # elevations[y][x]

    terrain = makePath(path, elevations, terrain)

    terrain.save(output)


# Simple function that returns the actual image
def getImage(imageFile):
    return Image.open(imageFile)


# Takes the file with the elevations and extracts the information needed
# for the program
#
# I know this is made pretty poorly and inefficient, but I was afraid of
# changing it and messing up the rest of my code
def getElevation(elevationsFile):
    elevations = []
    for i in range(500):
        elevations.append(0)

    file = open(elevationsFile)
    line = file.read().split()
    for i in range(500):
        temp = []
        for _ in range(395):
            temp.append(float(line.pop(0)))
        for _ in range(5):
            line.pop(0)
        elevations[i] = temp
    return elevations


# The function that does most of the work in the program
#
# Implements the A* Search and calls all the necessary helper functions
def makePath(path, elevations, terrain):
    pathFile = open(path)
    start = [pathFile.readline().split(), [[]]]

    frontier = PriorityQueue()  # coordinates to be popped
    frontier.put((0, start))
    explored = set()            # coordinates that have already been popped

    # looking back, this probably could have been done with a dictionary or set
    # but again, the code works well
    #
    # I'm not sure what I was thinking when doing this part
    curOrigin = [[0] * 500 for _ in range(500)]     # origins of each coordinate

    finalPath = []
    costs = {tuple(start[0]): 0}

    nextGoalCoord = pathFile.readline().split()
    while frontier.not_empty:       # main running loop

        coord = frontier.get()[1]   # pop an element, remove unwanted priority

        # This will be more clear later, when creating children
        curCoord = coord[0]         # Get just the actual coordinate
        if tuple(curCoord) not in explored:
            # Again, clearer later - save the origin
            curOrigin[int(curCoord[0])][int(curCoord[1])] = coord[1]

            if curCoord == nextGoalCoord:       # check for goal state

                # Have to reset all of the data for the next goal coordinate
                nextGoalCoord = pathFile.readline().split()
                frontier = PriorityQueue()
                frontier.put((0, coord))
                explored = set()
                costs = {tuple(curCoord): 0}
                # Add the coordinates to the final path
                finalPath.append(extractPath(curOrigin, curCoord, start))
                curOrigin = [[0] * 500 for _ in range(500)]
                start = [curCoord, 0]

                # If we finished the last goal coordinate -
                # print distance and draw path
                if not nextGoalCoord:
                    print(str(calcTotalDistance(finalPath, elevations)) + " m")
                    return modifyImage(terrain, finalPath)

            # If not in the goal state
            children = getChildren(curCoord)       # create children

            # For each child, we check if it is legal not already explored
            for child in children:
                if int(child[0][0]) >= 0 and int(child[0][1]) >= 0:
                    if int(child[0][0]) < 395 and int(child[0][1]) < 500:
                        if tuple(child[0]) not in explored:

                            # get the new cost of going to a child
                            childCost = getCost(curCoord, child[0], elevations,
                                                terrain)

                            # If a legal location - calculate g(n) by adding the
                            # new cost to the total cost of its parent
                            if childCost != -1:
                                costs[tuple(child[0])] = childCost + \
                                                         costs[tuple(curCoord)]
                            else:
                                costs[tuple(child[0])] = -1

                            # Calculate h(n)
                            # because the base multiplier for cost is 1
                            # can just use 3d distance
                            heuristic = getDistance(child[0], nextGoalCoord,
                                                    elevations)

                            # Place child in frontier with f(n) = g(n) + h(n)
                            if costs[tuple(child[0])] != -1:
                                frontier.put(
                                    (costs[tuple(child[0])] + heuristic, child))

            # Once all children are checked and added, the parent is done
            explored.add(tuple(curCoord))

    # A catch statement that should only occur if the path is impossible
    return modifyImage(terrain, finalPath)


# Function that returns a list of all potential children of a given node
# regardless of location
def getChildren(curCoord):
    # return 2d array of [[actual coord], [origin coord]]
    # As alluded to above, children are created with a connection to their
    # parent. This is so the origin does not need to be changed once popped

    # noinspection PyListCreation
    children = []

    # Cardinal
    children.append([[str(int(curCoord[0]) - 1), curCoord[1]], [curCoord]])
    children.append([[str(int(curCoord[0]) + 1), curCoord[1]], [curCoord]])
    children.append([[curCoord[0], str(int(curCoord[1]) - 1)], [curCoord]])
    children.append([[curCoord[0], str(int(curCoord[1]) + 1)], [curCoord]])

    # Diagonals
    children.append([[str(int(curCoord[0]) - 1), str(int(curCoord[1]) - 1)],
                     [curCoord]])
    children.append([[str(int(curCoord[0]) - 1), str(int(curCoord[1]) + 1)],
                     [curCoord]])
    children.append([[str(int(curCoord[0]) + 1), str(int(curCoord[1]) - 1)],
                     [curCoord]])
    children.append([[str(int(curCoord[0]) + 1), str(int(curCoord[1]) + 1)],
                     [curCoord]])

    return children


# Function that gets the cost of moving to a new child
# Note: This is not all of g(n) as this does not account for the cost of all
# previous ancestor nodes
def getCost(start, end, elevations, terrain):
    pixels = terrain.load()

    # get the 3d distance between a node and its child
    cost = getDistance(start, end, elevations)

    # figure out the terrain we are moving through
    # two steps because some testcases use RGB and some use RGBA
    # Or at least I think, I might be crazy
    terrainTypeTemp = pixels[int(end[0]), int(end[1])]
    terrainType = (terrainTypeTemp[0], terrainTypeTemp[1], terrainTypeTemp[2])

    # Multiply the cost of moving by a factor related to the terrain difficulty
    # These numbers are based on personal opinion and may not be 100% accurate
    # in terms of actual movement speed.
    if terrainType == (248, 148, 18):           # Open land
        cost = cost * 1.1
    elif terrainType == (255, 192, 0):          # Rough meadow
        cost = cost * 1.75
    elif terrainType == (255, 255, 255):        # Easy movement forest
        cost = cost * 1.25
    elif terrainType == (2, 208, 60):           # Slow run forest
        cost = cost * 1.5
    elif terrainType == (2, 136, 40):           # Walk forest
        cost = cost * 2
    elif terrainType == (5, 73, 24):            # Impassible vegetation
        cost = cost * 5
    elif terrainType == (0, 0, 255):            # Lake/Swamp/Marsh
        cost = cost * 10
    elif terrainType == (71, 51, 3):            # Paved Road - the standard
        cost = cost * 1
    elif terrainType == (0, 0, 0):              # Footpath
        cost = cost * 1.05
    else:                                       # Out of bounds or not listed
        return -1

    return cost


# Uses Pythagorean Theorem to calculate 3d distance between 2 points
def getDistance(start, end, elevations):
    start_x = int(start[0])
    start_y = int(start[1])

    end_x = int(end[0])
    end_y = int(end[1])

    change_x = abs(start_x - end_x) * 10.29
    change_y = abs(start_y - end_y) * 7.55

    dd_diagonal = math.sqrt((change_x ** 2) + (change_y ** 2))

    change_z = abs(int(elevations[start_y][start_x]) -
                   int(elevations[end_y][end_x]))

    distance = math.sqrt((change_z ** 2) + (dd_diagonal ** 2))

    return distance


# Given the list of saved origins, the end coord and the start coord -
# builds the path
def extractPath(origins, curCoord, start):
    nextSpot = origins[int(curCoord[0])][int(curCoord[1])][0]
    path = [curCoord]
    while nextSpot != start[0]:
        path.append(nextSpot)
        nextSpot = origins[int(nextSpot[0])][int(nextSpot[1])][0]
    path.append(start[0])
    path.reverse()
    return path


# Given the entire final path, sets all used pixels to red - an unused color
def modifyImage(image, finalPath):
    pixels = image.load()
    for path in finalPath:
        for coord in path:
            pixels[int(coord[0]), int(coord[1])] = (255, 0, 0, 255)
    return image


# Calculates the actual distance traveled
def calcTotalDistance(path, elevations):
    totalDistance = 0
    for i in range(len(path)):
        for j in range(len(path[i]) - 1):
            distance = getDistance(path[i][j], path[i][j + 1], elevations)
            totalDistance = totalDistance + distance
    return totalDistance


# On run, if there are not enough arguments, the program will give this message
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Please run with the format:")
        print("$python3 lab1.py terrain.png mpp.txt path.txt output.png")
    else:
        main()
