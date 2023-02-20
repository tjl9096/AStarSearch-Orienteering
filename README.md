# AStarSearch-Orienteering
Implementing A* graph search on given elevation and terrain data

As a lab for my Intro to AI class, we were required to implement the A* search algorithm to find an optimal path through different points on a map.

The information we were given for the lab was a visual map with colors corresponding to different terrain types, elevations of the terrain that do not match 1-1 with the pixel size of the terrain map given, and the points that the path needs to visit.

In order to implements A*, a heursitic is needed, of which straight 3d distance works best in this scenario. The heuritic, combined with the actual cost (in distance) of moving to a new square, allows for A* to be used.

Provided are a real world terrain and elevation maps, labeled as terrain.png and mpp.txt, as well as a few of the test cases that were given as a part of the lab.

To run, use "$python3 lab1.py terrain.png mpp.txt path.txt output.png" with 'path.txt' being the file of locations you want the path to hit and output.png being the name of the file you want the output to be. The output file will be an image of the terrain with the path created drawn as red. The code will also print the total distance of the path through basic output.

As a side note, after submitting the working code, I went back through and realized some extraneous and wasteful steps in my code. Namely, my parsing of the elevation file is very poorly done and a few of my data structures are used both ineffectively and/or could be replaced with more efficient ones. I have not made these changes as I have had other coding assignments to work on, but they would b e the first thing I would change if/when I come back to work on this project.
lkugf,k
