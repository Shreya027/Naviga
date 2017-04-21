'''
*Team Id: 1340
*Author List: Kanksha Zaveri, Romit Shah, Shreya Naik, Niti Shah
*
*Filename: RPIFINAL.py
*Theme: Navigate a Terrain
*Functions: move(), direction(), rgb(), goStraight(), no(), yes(),
            sendAcknowledgemnet(int status, socket connection), sendColour(int data, socket connection), main()
*Global Variables: NONE
*
'''

import socket
import sys
import numpy as np
import cv2
import time
from numpy import *
import math
import  RPi.GPIO as GPIO


'''
*Function Name: rgb()
*Input: None
*Output: Detects the checkpoint color and glows the corresponding LED
*Logic: For detecting the checkpoints:
        The bgr ranges for each color is added in a dictionary. The frames of the flex are continuously captured using the webcam.
        Each frame is masked and then the contours are applied according to each color's range. If we get contours for any particular
        color, area is calculated and the color having the maximum area is the checkpoint's color. 
        For glowing the LED:
        Once we get the correct color of the checkpoint, we have an associated rgb code with each color. This rgb code is a combination of 
        0's and 1's. 0 indicates that color has to be glowed and 1 indicates color doesn't have to be glowed. 
        Thus this way we obtain all 7 combinations for all 7 colors.
*Example Call: rgb()
'''

def rgb():
    redPin=11
    greenPin=10
    bluePin=12
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(redPin,GPIO.OUT)
    GPIO.setup(greenPin,GPIO.OUT)
    GPIO.setup(bluePin,GPIO.OUT)
    loop = 1
    maximum = 0
    vc = cv2.VideoCapture(0)
    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False
        #print "failed to open webcam"


    dict = {'p': [[117,72,172],[157,112,212]], 'b': [[97,12,42],[137,52,82]], 'c': [[130, 85, 43],[170, 125,83]],'g': [[64,139,57],[104,179,97]], 
    'y': [[19,132,119],[59,172,159]], 'r' : [[0,0,128],[0,0,255]],'w':[[0,0,0],[10,10,10]]}

    if rval == 1:
        while loop ==1:
            cv2.imshow("frame", frame)
            rval, frame = vc.read()
            keyy = cv2.waitKey(20)
            if keyy == 27:
                loop = 0
            
        for key, vals in dict.items():
            lower_Bound = vals[0]
            upper_Bound = vals[1]
            lowerBound=np.array(lower_Bound)
            upperBound=np.array(upper_Bound)
            mask = cv2.inRange(frame, lowerBound, upperBound)
            #cv2.imshow("mask", mask)
            contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            if contours!= []:
                cnt = contours[0]
                area = cv2.contourArea(cnt)
                #print ("Done")
                #print key
                #print area
                if area> maximum:
                    maximum = area
                    print key

                    if key == "r":
                        (r,g,b)=(0,1,1)
                    elif key=="g":
                        (r,g,b)=(1,0,1)
                    elif key=="c":
                        (r,g,b)=(1,0,0)
                    elif key=="y":
                        (r,g,b)=(0,0,1)
                    elif key=="b":
                        (r,g,b)=(1,1,0)
                    elif key=="p":
                        (r,g,b)=(0,1,0)
                    elif key=="w":
                        (r,g,b)=(0,0,0)

                    GPIO.output(redPin,r)
                    GPIO.output(greenPin,g)
                    GPIO.output(bluePin,b)
                    time.sleep(5)
                    GPIO.output(redPin,1)
                    GPIO.output(greenPin,1)
                    GPIO.output(bluePin,1)
                    return key

                    


                    
                    #print ('Max')
                    #print maximum
            #time.sleep(0.5)
        if maximum!=0:
            loop = 0

'''
*Function Name: direction()
*Input: The direction in which the rover should move in the form of an integer
*Output: The rover will move in the appropriate direction by calling the corresponding software PWM function on the raspberry pi 
*Logic: Direction can be of six forms: Forward, Backward, Forward and Backward Left, forward and Backward Right.
        The move() function calls the appropriate direction using the direction function and an if - else ladder is used to make the rover move in the correct
        direction. For the movement, software PWM of the raspberry pi is used. First,GPIO.setMode() is used to specify the numbering system being used.
        In this case, we are using BCM. GPIO pins 24,23,27 and 22 which correspond to pins 18,16,13 and 15 respectively are setup and PWM function is initialized.
        The start function is then called on each variable to set an initial value. It is set to 0 duty cycle here.
        ChangeDutyCycle function is then called according to the direction called to adjust the value of duty cycle.
        For eg, for moving the rover forward, we would need to move both the left and right in clockwise direction.
        Thus, the duty cycle for both L and R variable is set to 100 and the rover will thus move forward.
*Example Call: direction(1)
'''      
def direction(direction):
    print direction
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(24,GPIO.OUT)
    GPIO.setup(23,GPIO.OUT)
    GPIO.setup(27,GPIO.OUT)
    GPIO.setup(22,GPIO.OUT)
    PWMR=GPIO.PWM(24,60)
    PWML=GPIO.PWM(27,60)
    PWMR1=GPIO.PWM(23,60)
    PWML1=GPIO.PWM(22,60)
    PWMR.start(0)
    PWMR1.start(0)
    PWML.start(0)
    PWML1.start(0)
    print "starting"
    if (direction == 1): #foward
        PWMR.ChangeDutyCycle(70)
        PWML.ChangeDutyCycle(70)
        time.sleep(0.7)
        print direction
    elif(direction==2):#fright
        print direction
        PWML.ChangeDutyCycle(70)
        time.sleep(0.7)
    elif(direction==3):#fleft
        print direction
        PWMR.ChangeDutyCycle(70)
        time.sleep(0.7)
    elif(direction==4): #backward
        print direction
        PWMR1.ChangeDutyCycle(70)
        PWML1.ChangeDutyCycle(70)
        time.sleep(0.4)
    elif(direction==5): #bright
        print direction
        PWML1.ChangeDutyCycle(70)
        time.sleep(0.4)
    elif(direction==6): #bleft
        print direction
        PWMR1.ChangeDutyCycle(70)
        time.sleep(0.4)
    print "stopped"
    PWMR.stop()
    PWML.stop()
    PWMR1.stop()
    PWML1.stop()
    GPIO.cleanup()


'''
*Function Name: move()
*Input: None
*Output: The direction in which the rover should move. Returns 0 when movemnet is completed
*Logic: The webcam continuously captures frames of the flex and each frame is then converted to a gray image on which minMaxLoc function is applied.
        This minMaxLoc function basically identifies the spot with the minimum and maximum intensity in the image, and gives the intensity value and the 
        corresponding location. Since laser will always give the brightest intensity in the image, the maxLoc function gives us the exact location of 
        the laser. We get the row and column value using img.shape function. The frame captured is always divided into parts containing values like xDiv,
        yDiv which are 10% of teh image. It also has variables which store the centre coordinates of the frame.
        The location of laser is stored in laserLocationX and laserLocationY respectively. 
        Depending on the position of teh laser, the direction function is called to make it move forward, forward right, forward left, backward right, backward left.
*Example Call: move()
'''
def move():

    vc = cv2.VideoCapture(0)

    if vc.isOpened(): #try to get the first frame
        rval, frame=vc.read()
        time.sleep(1)

    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)             #Convert each frame to gray format
    (minVal,maxVal,minLoc,maxLoc)=cv2.minMaxLoc(gray)       #Apply the minMax Loc function
    if (maxVal >200):
        cv2.circle(frame,maxLoc,5,(255,0,0),2)
        cv2.imshow("Naive",frame)
    else:
        while(not(maxVal>200)):
            rval, frame=vc.read()
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)             #Convert each frame to gray format
            (minVal,maxVal,minLoc,maxLoc)=cv2.minMaxLoc(gray)       #Apply the minMax Loc function
        cv2.circle(frame,maxLoc,5,(255,0,0),2)
        cv2.imshow("Naive",frame)
    r,c=gray.shape 
    xcentre = c//2
    ycentre = r//2
    laserLocationX = maxLoc[0]
    laserLocationY = maxLoc[1]
    xDiv = c//10
    yDiv = r//10
    if(laserLocationY<ycentre):
        if(abs(laserLocationX-xcentre)<1.5*xDiv): #Laser in middle 30% above centre line
            direction(1) #Forward
        elif(laserLocationX>xcentre):
            direction(2) #Forward Right
        else:
            direction(3) #Forward Left
    else:
        if(abs(laserLocationX-xcentre)<1.5*xDiv): #Laser in middle 30% below centre line
            direction(4) #Backward
        elif(laserLocationX>xcentre):
            direction(5) #Backward Right
        else:
            direction(6) #Backward Left
    return 0
        
'''
*Function Name: goStraight()
*Input: None
*Output: Returns found when movement happens
*Logic: Calls move function which calls direction function to follow the laser
*Example Call: goStraight()
'''
def goStraight():
    print("Followed Laser")
    #Insert code to follow laser here
    #If laser not found, return 404, where found stores 404 or 0. Zero returned when everything is working fine.

    found = move()

    return found

'''
*Function Name: no()
*Input: None
*Output: Returns 0 because nothing must be done i.e. checkpoint not reached
*Logic: print statemnet
*Example Call: no()
'''
def no():
    print("No function to perform")
    return 0

'''
*Function Name: yes()
*Input: None
*Output: Returns 0 after printing that checkpoint is reached
*Logic: print statemnet
*Example Call: yes()
'''
def yes():
    print("Reached checkpoint yayy.")
    return 0

'''
*Function Name: sendAcknowledgement()
*Input: status -> What go straight returns (which is generally always zero when it successfully follows teh laser)
        connection -> Socket object used to send and receive data from laptop
*Output: Returns 0 and sends either an acknowledgement or z which means rover is lost
*Logic: Sends character to laptop depending on teh status of the rover
*Example Call: sendAcknowledgement()
'''
def sendAcknowledgement(status, connection):
    if (status == 0):
        connection.sendall('a')
    else:
        connection.sendall('z')
    return 0

'''
*Function Name: sendColour()
*Input: data -> depends on whether no or yes function was called
        connection -> Socket object used to send and receive data from laptop
*Output: Returns 0 and sends colour or f depending on whether colour is reached or not
*Logic: Sends character to laptop depending on whether checkpoint is reached or not
*Example Call: sendColour()
'''
def sendColour(data, connection):
    if (data=='t'):
        print("Colour will be sent")
        colour = rgb()
        connection.sendall(colour)
    else:
        connection.sendall('f')
        #Means I have not reached the checkpoint.
        
'''
*Function Name: main()
*Input: NONE
*Output: Socket begun, functions called control rover, when path is reached, socket closed.
*Logic: Creates and binds socket . Listens for incoming connections.
        Once sonnection is accepted to socket, starts sending and receiving data which will trigger specfic functions.
*Example Call: main()
'''
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 8000)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    sock.listen(1)

    status = 0
    goStraightStatus = 0
    i = 0;
    options = {'g':goStraight, 'f':no, 't':yes}
    while True:
        connection, client_address = sock.accept()
        try:
            data = connection.recv(1) #Take first input here
            print data
            while True:
                #If g is received, go straight. 
                #If f is received, no checkpoint. Else t is received so yes checkpoint.
                ###ONCE EVERYTHING IS RECEIVED AND FUNTIONS ARE PERFORMED###
                #Send acknowledgement
                #(Depending on whether f or t is received) Send colour or not applicable.
                i = i+1
                goStraightStatus = status #Since it comes second in the receiving thing, when i%3 happens this will have goStraight ka status only
                if(data=='g'):
                    status = goStraight()
                    i = 1
                elif(data=='f'):
                    status = no()
                elif(data=='t'):
                    status = yes()
                else:
                    print ("in else")
                    status = no();
                if(i%2==0):
                    i = 0
                    print("This is go straight status")
                    print goStraightStatus
                    sendAcknowledgement(goStraightStatus, connection)
                    sendColour(data, connection)
                data = connection.recv(1) #Receive next character
                print ("This is data ")
                print data

                if (data=='d'):                             #If d is received, we are done and reached final point.
                    break

        finally:
            sock.close()

if __name__ == '__main__':
    main()           ## Main function call
