'''
*Team id : 1340
*Author List : Kanksha Zaveri, Romit Shah, Shreya Naik, Niti Shah
*Filename : section2.py
*Theme : Navigate A Terrain
*Functions : sine(int), cosine(int), readImageBinary(string), readImageHSV(string), findNeighours(img,int,int,int), colourCell(img,int,int,int,int),
            buildGraph(img,int), findPath(dict,tuple,tuple), findMarkers(string, int), findStartPoint(img,int), findOptimumPath(list, int, tuple, img),
            colourPath(img, list, int, int), findCellnum(int, int), searchMin(dict), eachColor(img,list,list,int,int, int), main(string,int), 
*Global Variables : none
'''

import numpy as np
import cv2
import math
import time
import socket
import sys

'''
*Function Name : readImage
*Input : filePath - filepath of image as input
*Output : Returns the image in binary form
*Logic : This function reads an image from the specified filepath and changes colour space from from BGR to Grayscale. Then applies binary thresholding to the image.
        Function cv2.cvtColor(input_image, flag) is used, where flag determines the type of conversion. 
        Function cv2.threshold is used for thresholding.
*Example Call : readImage(filePath);
'''
def readImage(filePath):
    #############  Add your Code here   ###############
    img=cv2.imread(filePath)
    img[330,268]=[255,0,0]
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret,binaryImage=cv2.threshold(gray,127,255,cv2.THRESH_BINARY)

    ###################################################
    return binaryImage
'''
*Function Name : readImageHSV
*Input : filePath - filepath of image as input
*Output : Returns HSV equivalent of the image
*Logic : This function reads an image from the specified filepath and changes the color-space of it from BGR to HSV. Function cv2.cvtColor(input_image, flag)
        is used, where flag determines the type of conversion. 
*Example Call : readImageHSV(filePath); 
'''
def readImageHSV(filePath):
    mazeImg = cv2.imread(filePath)
    hsvImg = cv2.cvtColor(mazeImg, cv2.COLOR_BGR2HSV)
    return hsvImg

'''
*Function Name : sine
*Input : angle - value of angle
*Output :Returns sine of an angle
*Logic : We use math library function to calculate sine of an angle
*Example Call : sine(30); - will return 0.5 
'''
def sine(angle):
    return math.sin(math.radians(angle))

'''
*Function Name : cosine
*Input : angle - value of angle
*Output :Returns cosine of an angle
*Logic : We use math library function to calculate cosine of an angle
*Example Call : cosine(60); - will return 0.5
'''
def cosine(angle):
    return math.cos(math.radians(angle))

filePath1 = 'MAP.jpg'
filePath2 = 'MAPEDITED.jpg'

'''
* Function Name: findCellnum
* Input:level -> number of levels(1-6)
    thetaDegrees -> angle in degrees(0-360) going ANTICLOCKWISE from the positive y-axis 
* Output: returns the cellnumber whose who has the imput level and angle
* Logic: This function finds the cell number depending on the level and angle given. 
* Example Call: cellnum=findCellnum(3,270)-will return the cellnumber of the cell present at level 3 at an angle of 270
'''
def findCellnum(level, thetaDegrees):
    if level == 1:
        cellnum = thetaDegrees//90 + 1
    elif level == 2:
        cellnum = thetaDegrees//36 + 1
    elif (level == 3):
        cellnum = thetaDegrees//24 + 1
    else:
        cellnum = thetaDegrees//18 + 1
    return cellnum

'''
* Function Name: findCheckpoints
* Input: filePath -> stores path of image
         image -> stores our modified image with only checkpoints
* Output: returns a list of checkpoints
* Logic: FInds all teh contours and segregates them based on the area. Finds position of those specific contours since they would be markers
* Example Call: findCheckpoints(filePath1, res)
'''

def findCheckpoints(filePath, image):
    img = readImageHSV(filePath)
    h,w,c=img.shape
    list_of_checkpoints = []
    BREADTH = len(image)/20
    LENGTH = len(image[0])/20
    midPoint = 990/2
    contours, hierarchy = cv2.findContours(image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:        
        area = cv2.contourArea(cnt)
        if ((area<1000)&(area>100)):
            ## We calculate the centroid of the contours. That gives us the position of the marker
            M = cv2.moments(cnt)
            cx = (M['m10']/M['m00'])
            cy = (M['m01']/M['m00'])
            centroid = cx,cy
            cart_y=(BREADTH*cx)/h                                                       ## distance from left
            cart_x=(LENGTH*cy)/w                                                        ## distance from top
            left = cart_y*20                                                            ##distance from left in pixels
            top = cart_x*20                                                             ##distance from top in pixels
            level = math.sqrt((midPoint-top)*(midPoint-top) + (midPoint-left)*(midPoint-left))##find distance from centre to marker in pixels
            #Width of level 1 is 80 pixel, level 2 onwards each level's width is 100 pixel hence..
            if (level< 80):
                level = 1
            else:
                level = (level-80)//100                                                           ##Find level
                level = level +2
        
            if (top < len(image)/2)& (left > len(image)/2):                         #Quadrant 1
                tanTheta = float(midPoint-top)/(midPoint-left)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from x-axis
                theta = 270 + theta                                                     #Theta in anticlockwise direction from positive y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            elif (top < len(image)/2)& (left < len(image)/2):                       ##Quadrant 2
                tanTheta = float(midPoint-left)/(midPoint-top)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            elif (top > len(image)/2)& (left < len(image)/2):                       #Quadrant 3
                tanTheta = float(midPoint-top)/(midPoint-left)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from x-axis
                theta = 90+theta                                                        #Theta in anticlockwise direction from positive y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            else:                                                                   #Quadrant 4
                tanTheta = float(midPoint-left)/(midPoint-top)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from x-axis
                theta = 180+theta                                                       #Theta in anticlockwise direction from positive y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            list_of_checkpoints.append((int(level),int(cellnum)))

    return list_of_checkpoints

'''
* Function Name: findCheckpointsAngle
* Input: filePath -> stores path of image
         image -> stores our modified image with only checkpoints
* Output: returns a list of checkpoints with level, cell number and ALSO precise angle and dist in centimetre from teh centre
* Logic: FInds all teh contours and segregates them based on the area. Finds position of those specific contours since they would be markers. 
   Returns precise ocation of cehckpoint
* Example Call: findCheckpointsAngle(filePath1, res)
'''
def findCheckpointsAngle(filePath, image):
    img = readImageHSV(filePath)
    h,w,c=img.shape
    list_of_checkpoints = []
    BREADTH = len(image)/20
    LENGTH = len(image[0])/20
    midPoint = 990/2
    contours, hierarchy = cv2.findContours(image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:        
        area = cv2.contourArea(cnt)
        if ((area<1000)&(area>100)):
            ## We calculate the centroid of the contours. That gives us the position of the marker
            M = cv2.moments(cnt)
            cx = (M['m10']/M['m00'])
            cy = (M['m01']/M['m00'])
            centroid = cx,cy
            cart_y=(BREADTH*cx)/h                                                       ## distance from left
            cart_x=(LENGTH*cy)/w                                                        ## distance from top
            left = cart_y*20                                                            ##distance from left in pixels
            top = cart_x*20                                                             ##distance from top in pixels
            level = math.sqrt((midPoint-top)*(midPoint-top) + (midPoint-left)*(midPoint-left))##find distance from centre to marker in pixels
            #Width of level 1 is 80 pixel, level 2 onwards each level's width is 100 pixel hence..
            distInCm = (level*125)//495
            if (level< 80):
                level = 1
            else:
                level = (level-80)//100                                                           ##Find level
                level = level +2
        
            if (top < len(image)/2)& (left > len(image)/2):                         #Quadrant 1
                tanTheta = float(midPoint-top)/(midPoint-left)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from x-axis
                theta = 270 + theta                                                     #Theta in anticlockwise direction from positive y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            elif (top < len(image)/2)& (left < len(image)/2):                       ##Quadrant 2
                tanTheta = float(midPoint-left)/(midPoint-top)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            elif (top > len(image)/2)& (left < len(image)/2):                       #Quadrant 3
                tanTheta = float(midPoint-top)/(midPoint-left)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from x-axis
                theta = 90+theta                                                        #Theta in anticlockwise direction from positive y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            else:                                                                   #Quadrant 4
                tanTheta = float(midPoint-left)/(midPoint-top)                          #find tan theta
                if tanTheta<0:
                    tanTheta = tanTheta*-1
                theta = math.degrees(math.atan(tanTheta))                               #theta anticlockwise direction from x-axis
                theta = 180+theta                                                       #Theta in anticlockwise direction from positive y-axis
                #print theta
                cellnum = findCellnum(level, theta)
            list_of_checkpoints.append((level,cellnum, distInCm, int(theta)))

    return list_of_checkpoints

'''
* Function Name: getLevelInfo
* Input: level -> stores level
* Output: returns radius, number of cells and angle
* Logic: From map
* Example Call: getLevelInfo(2)
'''
def getlevelinfo(level):
    #r is radius, c is number of cells, a is angle
    if level==1:
        a=90
        c=4
        r=80
    elif level==2:
        c=10
        a=36
        r=180
    elif level==3:
        c=15
        a=24
        r=280
    elif level==4:
        c=20
        a=18
        r=380
    elif level==5:
        c=20
        a=18
        r=480
    return a,c,r

'''
*Function Name : findNeighbours
*Input : img - the maze image
         level - level number of the cell whose neighbours are to be found
         cellnum - Cell number of that cell
         size - size of the maze (being either 1 or 2)
*Output : List of cell which are traversable from specified cell
*Logic : img function takes in coordinates as arguments and returns the pixel intensity for the given coordinate.
        If the value returned is 0 ,then it means that the coordinate is black and hence a boundary exists.
*Example Call : findNeighbours(img,1,2); - will return a list of cells which are traversable from cell (1,2)
'''
def findNeighbours(img, level, cellnum):

    img1 = cv2.imread(filePath1)
    neighbours = []
    middle=495 

    ########FIND NEIGHBOURS AWAY FROM THE CENTER 
    #r is radius, c is number of cells, a is angle
    a1,c1,r1=getlevelinfo(level)
    if (level!=5):
        a2,c2,r2=getlevelinfo(level+1)
        xdistFromCenter = r1 * sine(cellnum * a1 - a1/2)
        ydistFromCenter = r1 * cosine(cellnum * a1 - a1/2)

        if xdistFromCenter <0:
            xdistFromCenter = xdistFromCenter*-1
        if ydistFromCenter <0:
            ydistFromCenter = ydistFromCenter*-1
    
        if((cellnum>c1/4)&(cellnum<=3*c1/4)):
            if ((level == 3)&(cellnum==4)):
                y = middle - ydistFromCenter
                y = y+2 #Because map pe it is more accurate for some reason
            else:
                y=middle + ydistFromCenter
                y = y-2 #Because map pe it is more accurate for some reason
        else:
            if ((level == 3)&(cellnum==11)):
                y=middle + ydistFromCenter
                y = y-2 #Because map pe it is more accurate for some reason
            else:
                y=middle - ydistFromCenter
                y = y+2 #Because map pe it is more accurate for some reason
            
        if (cellnum<=c1//2):
            x=middle - xdistFromCenter
            x = x+2
        else:
            x=middle + xdistFromCenter
            x = x-2

        out = img[y,x]
        if((img[y,x]!=0)&(img[y+1,x]!=0)&(img[y-1,x]!=0)&(img[y+2,x]!=0)&(img[y-2,x]!=0)&(img[y,x+1]!=0)&(img[y,x-1]!=0)&(img[y,x+2]!=0)&
           (img[y,x-2]!=0)&(img[y+3,x]!=0)&(img[y-3,x]!=0)&(img[y,x+3]!=0)&(img[y,x-3]!=0)):
            newcellnum=cellnum*c2//c1
            neighbours.append((level+1,newcellnum))

    ########FIND NEIGHBOURS ON LEFT AND RIGHT        
    
    if (cellnum == 1):
        neighbours.append((level,c1)) #Left neihbour
    else:
        neighbours.append((level,cellnum-1)) #Left neihbour
    neighbours.append((level,((cellnum)%c1)+1)) #right neighbours

    ########FIND NEIGHBOURS TOWARDS THE CENTER

    a2,c2,r2=getlevelinfo(level-1)
    xdistFromCenter = r2 * sine(cellnum * a1 - a1/2)
    ydistFromCenter = r2 * cosine(cellnum * a1 - a1/2)

    if xdistFromCenter <0:
        xdistFromCenter = xdistFromCenter*-1
    if ydistFromCenter <0:
        ydistFromCenter = ydistFromCenter*-1

    if((cellnum>c1/4)&(cellnum<=3*c1/4)):
        if ((level == 3)&(cellnum==4)):
            y = middle - ydistFromCenter
            y = y+2 #Because map pe it is more accurate for some reason
        else:
            y=middle + ydistFromCenter
            y = y-2 #Because map pe it is more accurate for some reason
        #print("Hey")
    else:
        if ((level == 3)&(cellnum==11)):
            y=middle + ydistFromCenter
            y = y-2 #Because map pe it is more accurate for some reason
        else:
            y=middle - ydistFromCenter
            y = y+2 #Because map pe it is more accurate for some reason
            
    if (cellnum<=c1//2):
        x=middle - xdistFromCenter
        x = x+2
        #cv2.circle(img,(int(x)+2,int(y)), 4, (20,130,25), -1)
        #print("Hi")
    else:
        x=middle + xdistFromCenter
        x = x-2

    if((img[y,x]!=0)&(img[y+1,x]!=0)&(img[y-1,x]!=0)&(img[y+2,x]!=0)&(img[y-2,x]!=0)&(img[y,x+1]!=0)&(img[y,x-1]!=0)&(img[y,x+2]!=0)&
       (img[y,x-2]!=0)&(img[y+3,x]!=0)&(img[y-3,x]!=0)&(img[y,x+3]!=0)&(img[y,x-3]!=0)):
        if level == 5:
           neighbours.append((level-1,cellnum)) 
        if level==4:
            if cellnum%4==0:
                neighbours.append((level-1,(cellnum//4)*3))
            if cellnum%4 == 1:
                neighbours.append((level-1,(cellnum//4)*3+1))
            if cellnum%4 == 3:
                neighbours.append((level-1, (cellnum//4)*3-1))
        if level == 3:
            if cellnum%3 == 0:
                neighbours.append((level-1,(cellnum//3)*2))
            if cellnum%3 == 1:
                neighbours.append((level-1,(cellnum//3)*2 + 1))
    if level == 2:
        if (cellnum == 1) | (cellnum == 2) | (cellnum == 3):
            neighbours.append((level-1, 1))
        if (cellnum == 3) | (cellnum == 4) | (cellnum == 5):
            neighbours.append((level-1, 2))
        if (cellnum == 6) | (cellnum == 7) | (cellnum == 8):
            neighbours.append((level -1, 3))
        if (cellnum == 8) | (cellnum == 9) | (cellnum == 10):
            neighbours.append((level-1, 4))
        
        
    return neighbours


'''
*Function Name : buildGraph
*Input : NONE
*Output : Returns the graph of the maze image in the form of a dictionary where the key is the cell and it's value is it's neighbours.
*Logic : First we create a list of all the cells in the maze.
         Second we find the neighbours of each individual cell and store it in another list.
         A dictionary is created by mapping the cells with their respective neighbours (by merging the 2 lists).
*Example Call : buildGraph(); - will return a graph in the form of a dictionary for the maze 
'''

def buildGraph():
    
    graph = {}
    img = readImage(filePath1)
    #   li is a list containing all the coordinates of the maze.
     #  Since each level has different no of cells , we have used different for loops for the same.

    li = []
        
    for i in range (1,11):          # for level 2
        li.append((2,i))
        
    for i in range (1,16):          # for level 3
        li.append((3,i))
        
    for i in range (1,21):          # for level 4 and 5
        li.append((4,i))
    for i in range(1, 21):
        li.append((5,i))

   
    #CREATES A LIST OF LISTS, WHERE EACH LIST INSIDE CONSISTS NEIGHBOURS OF CELLS IN ORDER
        
    val = []
    for cell in li:
        #print cell
        level = cell[0]
        cellnum = cell[1]
        neighbours = findNeighbours(img, level, cellnum)
        val.append(neighbours)

    for i in range(1,5):
        li.append((1,i))
        val.append([(0,0)])
    
    #LIST OF CELLS IS KEYS, LIST OF NEIGHBOURS ARE MY VALUES. MERGE THEM
    graph = dict(zip(li, val))
    return graph

'''
* Function Name: searchMin
* Input:myDictionary -> A dictionary which stores the coordinates of markers as keys and a tuple (total_path_length, path) as it's values
        where path stores list of coordinates.
* Output: returns the dictionary element, both key and value, which has the minimum path.
* Logic: This function searches the Dictionary for the least path length and updates small accordingly.
* Example Call: node=searchMin(myDictionary)
'''
def searchMin(myDictionary):
    small = myDictionary.items()[0]             #initialise small to first element
    for key, val in myDictionary.iteritems():
        if val[0] < small[1][0]:                #If the length of path of element is less than small
            small = (key, val)                  #update small
    return small

'''
*Function Name : findPath
*Input : graph -> takes in the graph form (dictionary) of the maze image built using the buildGraph function
         start -> specifies the initial point from which the shortest path has to be calculated
         end -> specifies the final point till which the shortest path has to be calculated
         path -> initially stores an empty list, and the list keeps appending the coordinates of the path recursively
*Output : Accepts arguments from user and returns the shortest path between two coordinates in the maze 
*Logic : It is a recursive function. Shortest keeps getting updated if the path is the shorter than any previous path tried.
*Example Call : findPath(graph,(2,2),(0,0)); - will return a list which contains a set of coordinates from (2,2) to (0,0) which is the shortest path between these points.
'''
def findPath(graph, start, end, path=[]): ## You can pass your own arguments in this space.
    #############  Add your Code here   ###############
    path = path + [start]                                       #adds the cell coordinates to path
    if start == end: 
        return path                                             #when done, returns path
    if not graph.has_key(start):  
        return None                                             #Returns NULL if the cell isn't present in our maze
    shortest = None                                             
    for node in graph[start]:
        if node not in path:                                    #if node hasn't been visited before
            newpath = findPath(graph, node, end, path)          #Recursively find path from there to end
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath                          
    ###################################################
    return shortest 


def findOptimumPath(listOfMarkers):     ## You can pass your own arguments in this space.
    path_array = []
    #############  Add your Code here   ###############

    graph = buildGraph()
    initial_point = (5,1)
    final_point = (1,2)
    imgBinary = readImage(filePath1)
    newList = []
     
    #CREATE myDictionary
    listIWant = listOfMarkers           #This is my list of keys
    for i in listIWant:
        newList.append(i) 
    listIWant.insert(0, initial_point)  #Add starting point (bottom left corner) to the list  
    length = len(listIWant)             #Finds total keys

    meaning = []                        #List for values of all the keys
    empty = []                  
    
    while length!=0:
        meaning.append((10000, None, empty))    #Each value has an integer, parent and list. First integer is size of path so far.
                                                #The list stores the path.
                                                #Value for every key of the dictionary is initialised here.
        length = length -1
    myDictionary = dict(zip(listIWant, meaning))    #Combining list of keys and values to get a dictionary
    myDictionary[initial_point] = (0,None,empty)    #Initialising starting point's size of path to 0
    #CREATION OF DICTIONARY ENDS
    
    while bool(listIWant):
        nodeTuple = searchMin(myDictionary)             #Calls function that returns a dictionary element having minimum size of path
        node = nodeTuple[0]                             #Node stores the key of element having minPath.
        parent = nodeTuple[1][1]                        #parent of element
        storedPath = nodeTuple[1][2]                    #List which stores path
        del myDictionary[node]                          #Deletes node from dictionary
        listIWant.remove(node)                          #Deletes node from list of keys
        if parent is not None:                          #If there is a parent of our element
            path_array.append(storedPath)               #Since there is no backtracking
        prev = node                                     #previous is now current node
        for v in listIWant:
            x = listIWant[0]                            #Stored only because I'll need last element eventually
            path = findPath(graph, node, v)             #Finds path between every node not traversed and current node
            myDictionary[v] = (len(path), node, path)   #Changes values in dictionary

    #THIS IS TO GO TO END AFTER COLLECTING ALL THE MARKERS            
    shortest = None
    for a in newList:
        path = findPath(graph, a, final_point)          #Finds path between end and every marker 
        if path:
            if not shortest or len(path) < len(shortest):
                shortest = path                         
                lastNode = a                            #lastNode is a, where a is the merker from where end has the shortest path
    if x == lastNode:                                   #If lastNode and the last marker I went to is the same
        path_array.append(shortest)
    else:
        path1 = findPath(graph, x, lastNode)            #Find path from last marker I went to, to the node from where end is shortest
        path1.pop()
        path1.extend(shortest)
        path2 = findPath(graph, x, final_point)         #Find path from last marker to end
        if len(path2) < len(path1):                     #append the shorter one to my main list
            path_array.append(path2)
        else:
            path_array.append(path1)
    ###################################################
    return path_array

'''
*Function Name : move()
*Input : cellLoc -> position to be reached of rover
         start -> Current position of rover
         sock -> socket connection to nodeMCU
*Output : Returns cellLoc stored in prev and degree to be traversed to go to cellLoc. 
*Logic : Based on where the rover has to go next, anticlockwise/clockwise direction is sent, panServo/tilTServo signal is sent
         And degree to be traversed is sent
*Example Call : move((2,3), (2,2), sock)
'''
def move(cellLoc, prev, sock):
    level = cellLoc[0]
    cellNumber = cellLoc[1]
    print prev[1]
    print cellLoc
    if(level == prev[0]):
        if(cellNumber == prev[1]+1):
            sock.sendall('a'); #anticlokwise
        else:
            sock.sendall('r'); #clockwise
        sock.sendall('o'); #panServo
        if level==5 or level == 4: 
            degree = 18
            degree1 =1
            degree2=8
        elif level==3:  
            degree = 24
            degree1=2
            degree2=4
        elif level==2:
            degree = 36
            degree1=3
            degree2=6
        elif level==1:
            degree = 90
            degree1=9
            degree2=0
        sock.sendall(str(degree1));
        sock.sendall(str(degree2));
        print ('sent')
    else:
        if(level > prev[0]):
            sock.sendall('r');
        else:
            sock.sendall('a');
        sock.sendall('t'); #tiltServo
        sumLevels = level + prev[0]
        print("this is sumLevels")
        print sumLevels
        if sumLevels==9: 
            degree = 8
            degree1=0
            degree2=8
        elif sumLevels==7:
            degree = 10
            degree1=1
            degree2=0
        elif sumLevels==5: 
            degree = 12
            degree1=1
            degree2=2
        elif sumLevels==3: 
            degree = 22
            degree1=2
            degree2=2
        sock.sendall(str(degree1));
        sock.sendall(str(degree2));
        print ('sent2')
    prev = cellLoc;
    return (prev, degree)

'''
*Function Name : checkpoint()
*Input : cellLoc -> position to be reached of rover
         start -> Current position of rover
         sock -> socket connection to nodeMCU
         index -> index in list of checkpoints
*Output : Returns cellLoc stored in prev and degree to be traversed to go to cellLoc. 
*Logic : Based on where the rover has to go next, anticlockwise/clockwise direction is sent, panServo/tilTServo signal is sent
         Degree to be traversed till checkpoint is sent alongwith degree till end of cell from checkpoint
*Example Call : checkpoint((2,3), (2,2), sock)
'''
def checkpoint(cellLoc, prev, sock, index, preciseListofCheckpoints):
    level = cellLoc[0]
    cellNumber = cellLoc[1]
    preciseCell = preciseListofCheckpoints[index]
    preciseAngle = preciseCell[3] #Angle from y to checkpoint
    preciseDist = preciseCell[2]                 ############################# TO BE IMPLEMENTED LATER
    if(level == prev[0]):
        if(cellNumber == prev[1]+1):
            sock.sendall('a');
        else:
            sock.sendall('r'); 
        sock.sendall('o');
        #degree is angle to move to go till next cell
        if level==5:
            degree=18
            preciseAngle = preciseAngle%degree
            
            degree2 = degree-int(preciseAngle) 
            #dist = 108.58
        elif level == 4:
            degree=18
            preciseAngle = preciseAngle%degree
            degree2 = degree-int(preciseAngle) 
            #dist = 83.33
        elif level==3:  
            degree=24
            preciseAngle = preciseAngle%degree
            degree2 = degree-int(preciseAngle) 
            #dist = 58
        elif level==2:
            degree=36
            preciseAngle = preciseAngle%degree
            degree2 = degree-int(preciseAngle) 
            #dist = 33
        elif level==1:
            degree=90
            preciseAngle = preciseAngle%degree
            degree2 = degree-int(preciseAngle) 
            #dist = 10
        preciseAngleTens = int(preciseAngle)/10
        preciseAngleOnes = int(preciseAngle)%10
        degree2Tens = degree2/10
        degree2Ones = degree2%10
        sock.sendall(str(preciseAngleTens))
        print preciseAngleTens
        sock.sendall(str(preciseAngleOnes))
        print preciseAngleOnes
        print degree2Tens
        print degree2Ones
        sock.sendall(str(degree2Tens));
        sock.sendall(str(degree2Ones));
        print ('sent')
    else:
        if(level > prev[0]):
            sock.sendall('r');
        else:
            sock.sendall('a');
        sock.sendall('t');
        sumLevels = level + prev[0]
        if sumLevels==9: 
            degree=8 
            preciseAngle = preciseAngle%degree
            degree2 = degree-preciseAngle       
        elif sumLevels==7:
            degree=10
            preciseAngle = preciseAngle%degree
            degree2 = degree-preciseAngle 
        elif sumLevels==5: 
            degree=12
            preciseAngle = preciseAngle%degree
            degree2 = degree-preciseAngle 
        elif sumLevels==3: 
            degree=22
            preciseAngle = preciseAngle%degree
            degree2 = degree-preciseAngle 
        preciseAngleTens = preciseAngle/10
        preciseAngleOnes = preciseAngle%10
        degree2Tens = degree2/10
        degree2Ones = degree2%10
        sock.sendall(str(preciseAngleTens))
        sock.sendall(str(preciseAngleOnes))
        sock.sendall(str(degree2Tens));
        sock.sendall(str(degree2Ones));
        print ('sent2')
    prev = cellLoc;
    return (prev, degree)

'''
*Function Name : transferData
*Input : sock2-> socket connection to rPi
         sock -> socket connection to nodeMCU
*Output : Returns nothing 
*Logic : This function gets called at every degree of movement of the laser.
         Laptop has sent data to nodeMCU to move laser. 
         Now nodeMCU sends laptop message to follow laser.
         nodeMCU sends laptop whether it has reached checkpoint or not.
         Laptop forwards message to rover.
         Laptop sends checkpoint(orNOT) to rover.
         Laptop receives acknowledgement of movement from rover.
         Laptop also receives colour or nothing from rover.
         Latop sends both those things back to nodeMCU.
*Example Call : transferData(sock, sock2)
'''
def transferData(sock, sock2):
    goStraight = sock.recv(1)
    sock2.sendall(goStraight)
    checkpointBool = sock.recv(1)
    sock2.sendall(checkpointBool)
    acknowledgement = sock2.recv(1)
    while(not((acknowledgement=='a')or(acknowledgement=='z'))):
        acknowledgement2 = sock2.recv(1)
        acknowledgement = acknowledgement2
    sock.sendall(acknowledgement)
    colour = sock2.recv(1)
    while(not((colour=='f')or(colour=='r')or(colour=='g')or(colour=='b')or(colour=='y')or(colour=='p')or(colour=='c')or(colour=='w'))):
        colour2 = sock2.recv(1)
        colour = colour2
    sock.sendall(colour)

'''
*Function Name: main()
*Input: NONE
*Output: NONE but mainly controls communication and sends data to nodeMCU and rover.
*Logic: Socket is begun, nodeMCU connected, functions are called, when path is reached, socket closed.
         Connected to socket of rPi.
         At every coordinate, there is communication and acknowledgement of movement from both - nodeMCU and rover in some
         form or the other. Characters are sent for communication and each character calls some function.
         Path is previously calculated from image processing techniques and functions.
*Example Call: main()
'''
def main():                 
    img = readImage(filePath1)
    img2 = readImage(filePath2)
    res = cv2.bitwise_xor(img,img2)
    res = cv2.bitwise_not(res)
    listofMarkers = findCheckpoints(filePath1, res)
    preciseListofCheckpoints = findCheckpointsAngle(filePath1, res)
    print(listofMarkers)
    #graph = buildGraph();
    #print graph
    list1 = []

    for element in listofMarkers:
        list1.append(element)

    path = findOptimumPath(listofMarkers)
    print path

    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to nodeMCU
    server_address = ("192.168.10.15", 5557)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)     

    # Connect the socket to rover
    serveraddress2 = ('192.168.10.1', 8000)
    print >>sys.stderr, 'connecting to %s port %s' % serveraddress2
    sock2.connect(serveraddress2)

    try:
    
        # Send data

        prev = (5, 1);
        #data = sock.recv(1)
        #print ("Data Received")
        #if (data != 's'):
        #  print("Wrong siganl received")
        
        for pathTillCheckpoint in path:
            print("PathTillcheckpoint")
            print pathTillCheckpoint
            for cellLoc in pathTillCheckpoint:
                print ("this is cell loc")
                print cellLoc
                if (cellLoc==prev):
                    sock.sendall('s')
                    print("same cell")
                elif cellLoc in list1:
                    print ("Reached checkpont")
                    sock.sendall('c')
                    index = list1.index(cellLoc)
                    prev, degree = checkpoint(cellLoc, prev, sock, index, preciseListofCheckpoints)
                    while(degree!=0):
                        transferData(sock, sock2)
                        degree=degree-1
                        print degree
                else:
                    sock.sendall('m')
                    prev, degree = move(cellLoc, prev, sock)
                    print ("This is previous")
                    print prev
                    print degree           
                    while(degree!=0):
                        transferData(sock, sock2)
                        degree=degree-1
                        print degree
                data = sock.recv(1)
                if (data == 's'):
                    print("Acknowledged properly")

    finally:
        print >>sys.stderr, 'Closing socket'
        sock.close()
    
    
    ## The main() function is called here. Specify the filepath of image in the space given.            
if __name__ == '__main__':
    main()           ## Main function call
    cv2.waitKey(0)
    cv2.destroyAllWindows()
