/*
 * Team Id: NT#1340
 * Author List: Shreya Naik, Niti Shah, Romit Shah, Kanksha Zaveri
 * Filename: clientserver.ino
 * Theme: Navigate A Terrain
 * Functions: setup(), led(), lost(), threshold(),  movee(WiFiClient, int), checkpoint(WiFiClient, int), samecell(WiFiClient), loop()
 * Global Variables: k, posPan, posTilt, pos, ssid, pass, server
 */
#include<SPI.h>
#include <ESP8266WiFi.h>
#include<Servo.h>

Servo panservo;
Servo tiltservo;

int k;
int posPan = 180;
int posTilt = 164;

char ssid[] = "RPi-1340";      // your network SSID (name)
char pass[] = "firebird";   // your network password

WiFiServer server(5557);

/*
 * Function Name: setup
 * Input: NONE
 * Output: Connects to Wifi and begins server
 * Logic: Both servos are attached to specific GPIO pins. 
 *        Uses library function to connect to Wifi - SSID and password are given. 
 *        Server is begun.
 * Example Call: Doesn't need to be called. (First setup gets called automatically, then loop)
 */ 
void setup() {
  panservo.write(posPan);
  tiltservo.write(posTilt);
  pinMode(2, OUTPUT);
  panservo.attach(4);
  tiltservo.attach(5);
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.print("Attempting to connect to SSID: ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  delay(10000);
  // attempt to connect to Wifi network:
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }
  server.begin();
  // you're connected now, so print out the status:
  printWifiStatus();
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void led()
{
  digitalWrite(2, HIGH);
  delay(1000);
  digitalWrite(2, LOW);
}

/*
 * Function Name: lost
 * Input: WiFiClient laptop
 * Output: Prints "I am lost" to laptop
 * Logic: client.print()
 * Example Call: lost(laptop);
 */
void lost(){
  Serial.println("I am lost");
}

/*
 * Function Name: threshold
 * Input: NONE
 * Output: Tilts laser such that it points at the same point it used to.
 * Logic: Need this function for when a servo has to rotate in one direction for more than 180 degree.
 *        1. FInd angle between centre of maze and current position of tilt servo.
 *        2. Tilt it twice that angle in the other hemisphere.
 *        This way after having panned 180 degree in the opposite direction (which is when this function is called), the laser will point back to where it was pointing initially.
 * Example Call: threshold();
 */ 
void threshold()
{
  if (posTilt<90) //Checks which half tiltServo is in
  {
    for(k=posTilt+1; k<posTilt+(2*(90-posTilt))+1; k++) //Accordingly shifts it like a pendulum would move to the other end
    {
      tiltservo.write(k);
    }
    posTilt = posTilt + (2*(90-posTilt)); //Update posTilt
  }
  else
  {
    for(k=posTilt-1; k>posTilt-(2*(posTilt-90))-1; k--) //Accordingly shifts it like a pendulum would move to the other end
    {
      tiltservo.write(k);
    }
    posTilt = posTilt - (2*(posTilt-90)); //Update posTilt
  }
}

/*
 * Function Name: movee
 * Input: WiFiClient laptop, int flag
 * Output: Moves from one cell to another, degree by degree after receiving information from laptop and getting an acknowledgement from rPi through laptop.
 * Logic: Is allowed to accept only two things in switch case - Firstly either 'r' or 'a'. 'r' stands for clockwise and 'a' for anticlockwise.  
 *        Secondly it can accept 'o' or 't' - 'o' means only pan needed to go to next cell, 't' means only tilt needed to go to next cell.
 *        In both 'o' and 't', clockwise or anticlockwise movement is checked and they are moved accordingly.
 *        Degree is received.
 *        At ever degree:
 *        1. server threshold is checked 9along with degrees greater than 180 or lesser than 0)
 *        2. 'g' is sent to laptop (which will send it to rpi) which means go. Servo is moved.
 *        3. 'f' is sent to laptop (which will send it to rpi) which means no checkpoint.
 *        4. 'a' or 'z' is received. In case garbage is received, we delay and read again. 'a' means acknowledged. 'z' means lost.
 *        5. Either 'f' or specific characters for colours received. In case garbage is received, we delay and read again. ('f' will only be received which means no colour)
 *        6. positions of servers updated
 *        Finally s is sent to laptop which basically is to acknowledge that NodeMCU has finished moving through the cell.
 * Example Call: flag = movee(laptop, flag);
 */ 
int movee(WiFiClient laptop, int flag){
  int count=0, i, rotation, j;
  if(laptop.connected()){
    do {
      if (laptop.available()) {
        char a = laptop.read(); 
        Serial.println("See what goes in switch case");
        Serial.write(a);
        switch(a)
        {
          case 'r':
            rotation = 1; //clockwise
            break;
          case 'a':
            rotation = 0; //anticlockwise
            break;
          case 'o': //panServo is to be moved
            if (laptop.available()) {
              
              char ten = laptop.read();
              int tens = (int)ten - 48;
              char one = laptop.read();
              int ones = (int)one - 48;
              int panDegree = tens*10 + ones; //Calulates pan degree since it is accepeted bit by bit as a string
              //Serial.println(panDegree);
              if (rotation == 1)  //If it has got the signal to move in the clockwise direction 
              {
                for(i=posPan; i<panDegree + posPan; i++)
                {
                  //The servo's threshold
                  if(i==180)
                  {
                    for(j = 180; j>=0; j--)
                    {
                      panservo.write(j);
                    }
                    threshold();
                  }
                  //If i goes beyond 180 degree, we've gone back to position 0 for servo. Thus i%180.
                  if(i>180)
                  {
                    laptop.write('g'); //Ask the laptop to go straight
                    
                    panservo.write(i%180);

                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  }
                  else
                  {
                    laptop.write('g'); //Ask the laptop to go straight
                    
                    panservo.write(i);

                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  }
                }
                posPan = (posPan + panDegree)%180; //Update posPan
              }
              else //anticlockwise panServo
              {
                
                if(posPan==0)
                  {
                    //Make it go 180 in opposite direction
                    for(j = 0; j<=180; j++)
                    {
                      panservo.write(j);
                    }
                    threshold();
                    posPan = 180;
                  }
                for(i=posPan; i>posPan - panDegree; i--)
                {
                  //The servo's threshold has reached
                  if(i==0)
                  {
                    //The servo's threshold when it has already covered 180 degree
                    for(j = 0; j<=180; j++)
                    {
                      panservo.write(j);
                    }
                    threshold();//Will make tilt go the other direction like pendulum so we come back to same position
                  }
                  
                  //If i goes till 0 degrees, we've gone back to position 180 degree for servo as seen above. Thus i+180. 
                  if(i<0)
                  {
                    laptop.write('g'); //Ask the laptop to go straight
                    panservo.write(i+180);
                    
                    ////delay(2000);

                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  }
                  else
                  {
                    Serial.println(i);
                    laptop.write('g'); //Ask the laptop to go straight
                    
                    panservo.write(i);
                    
                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                    //Already know that checkpoint isn't here so will not bother putting the if else on 'l' in movee anywhere.
                  }
                }
                //Update posPan
                if (posPan<panDegree) 
                  posPan = 180 - (panDegree-posPan);
                else
                  posPan = posPan - panDegree;
              }
            }
            break;
          case 't':
            delay(2000);
            if (laptop.available()) {
              char ten = laptop.read();
              int tens = (int)ten - 48;
              char one = laptop.read();
              int ones = (int)one - 48;             
              int tiltDegree = tens*10 + ones; //Since degree is accepted bit by bit and in string form
              if (rotation == 1) //That means going to a greater/outer level
              {
                if (posTilt>90) 
                {
                  for(k=posTilt; k<posTilt+tiltDegree; k++)
                  {
                    laptop.write('g'); //Ask the laptop to go straight
                    tiltservo.write(k);

                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  }
                  posTilt = posTilt + tiltDegree;
                }
                else
                {
                  for(k=posTilt; k>posTilt-tiltDegree; k--)
                  {
                    laptop.write('g'); //Ask the laptop to go straight
                    tiltservo.write(k);
                    //////delay(2000);

                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  }
                  posTilt = posTilt - tiltDegree; //Update posTilt
                } 
              }
              else //Going to level towards centre
              {
                if (posTilt<90)
                {
                  for(k=posTilt; k<posTilt+tiltDegree; k++)
                  {
                    laptop.write('g'); //Ask the laptop to go straight
                    tiltservo.write(k);
                    ////delay(2000);

                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  }
                  posTilt = posTilt + tiltDegree; //Update posTilt
                }
                else
                {
                  for(k=posTilt; k>posTilt-tiltDegree; k--)
                  {
                    laptop.write('g'); //Ask the laptop to go straight
                    tiltservo.write(k);
                    ////delay(2000);

                    laptop.write('f'); //Tell laptop it hasn't raeched a checkpoint (since move is called only when cell hasn't reached a checkpoint)
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  }
                  posTilt = posTilt - tiltDegree; //Update posTilt
                } 
            }
        }
        break;
      }
      count++;
    }
   }while(count<2);
  }
  laptop.write('s'); //Send next coordinates. Laptop will send 'm' or 'c' or 's' to call movee/checkpoint/samecell function and then the next set of coordinates as usual.
  return flag;
}

/*
 * Function Name: checkpoint
 * Input: WiFiClient laptop, int flag
 * Output: Moves from one cell to another, degree by degree after receiving information from laptop and getting an acknowledgement from rPi through laptop. 
 *        Apart from that, checkpoint colour LED is lit up when checkpoint is reached.
 * Logic: Is allowed to accept only two things in switch case - Firstly either 'r' or 'a'. 'r' stands for clockwise and 'a' for anticlockwise.  
 *        Secondly it can accept 'o' or 't' - 'o' means only pan needed to go to next cell, 't' means only tilt needed to go to next cell.
 *        In both 'o' and 't', clockwise or anticlockwise movement is checked and they are moved accordingly.
 *        Degree till checkpoint is accepted.
 *        Degree beyond to reach end of cell is accepted.
 *        At ever degree:
 *        1. server threshold is checked (along with degrees greater than 180 or lesser than 0)
 *        2. 'g' is sent to laptop (which will send it to rpi) which means go. Servo is moved.
 *        3. 'f' is sent to laptop (which will send it to rpi) which means no checkpoint UNLESS degree till checkpoint is reached in which case only 't' will be sent..
 *        4. 'a' or 'z' is received. In case garbage is received, we delay and read again. 'a' means acknowledged. 'z' means lost.
 *        5. Either 'f' (when no checkpoint reached) or specific characters for colours received (when checkpoint reached). 
 *           In case garbage is received, we delay and read again. If colour is received, RGB LED is lit up of that colour.
 *        6. positions of servers updated
 *        Finally s is sent to laptop which basically is to acknowledge that NodeMCU has finished moving through the cell.
 * Example Call: flag = checkpoint(laptop, flag);
 */ 
int checkpoint(WiFiClient laptop, int flag){
  int count=0, i, rotation, j;
  if (laptop.connected()){
    do {
      if (laptop.available()) {
        char a = laptop.read();
        Serial.write(a);
        switch(a)
        {
          case 'r':
            rotation = 1; //clockwise
            break;
          case 'a':
            rotation = 0; //anticlockwise
            break;
          case 'o': //panServo
            if (laptop.available()) {
         
              char ten = laptop.read();
              int tens = (int)ten - 48;
              char one = laptop.read();
              int ones = (int)one - 48;
              int panDegree = tens*10 + ones; //Degree from current position to checkpoint
              char ten2 = laptop.read();
              int tens2 = (int)ten2 - 48;
              char one2 = laptop.read();
              int ones2 = (int)one2 - 48;
              int panDegree2 = tens2*10 + ones2;//Degree from checkpoint to end of cell
              if (rotation == 1) //If clockwise movement
              {
                for(i=posPan; i<panDegree+panDegree2 + posPan; i++)
                {
                  //The servo's threshold
                  if(i==180)
                  {
                    for(j = 180; j>=0; j--)
                    {
                      panservo.write(j);
                    } //make panServo go the otehr way 
                    threshold(); //Make tilt move the other way same degree away
                  }
                  //If i goes beyond 360 degree, we've gone back to position 0 for servo. Thus i%360.
                  if(i>180)
                  {
                    laptop.write('g');
                    panservo.write(i%180);
                    if (i==(panDegree+posPan)%180)
                      laptop.write('t'); //Checkpoint reached. You need to send me colour instead of false now.
                    else
                      laptop.write('f'); //Ask the laptop to go straight
                    
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                    if (l!='f')
                      led();
                  }
                  else
                  {
                    laptop.write('g');
                    panservo.write(i);
                    if (i==(panDegree+posPan)%180)
                      laptop.write('t'); //Checkpoint reached. You need to send me colour instead of false now.
                    else
                      laptop.write('f'); //Ask the laptop to go straight
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                    if (l!='f')
                      led();
                  }
                }
                posPan = (posPan + panDegree+ panDegree2)%180; //Update posPan
              }
              else //anticlockwise panServo 
              {
                for(i=posPan; i>posPan - panDegree - panDegree2; i--)
                {
                  //The servo's threshold has reached
                  if(i==0)
                  {
                    for(j = 0; j<=180; j++)
                    {
                      panservo.write(j);
                    }
                    threshold();
                  }
                  //If i goes till 0 degrees, we've gone back to position 360 degree for servo as seen above. Thus i+360. 
                  if(i<0)
                  {
                    laptop.write('g');
                    panservo.write(i+180);
                    if ((i==posPan -panDegree)||(i == panDegree-posPan))//To check both signs
                      laptop.write('t'); //Checkpoint reached. You need to send me colour instead of false now.
                    else
                      laptop.write('f'); //Ask the laptop to go straight
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                    if (l!='f')
                      led();
                      //LED code goes here
                  }
                  else 
                  {
                    laptop.write('g');
                    panservo.write(i);
                    if ((i==posPan -panDegree)||(i == panDegree-posPan))
                      laptop.write('t'); //Checkpoint reached. You need to send me colour instead of false now.
                    else
                      laptop.write('f'); //Ask the laptop to go straight
                    char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                    if (l!='f')
                      led();
                      //LED code here
                  }
                }
                //Update posPan
                if (posPan<panDegree+panDegree2)
                  posPan = 180 - (panDegree + panDegree2-posPan);
                else
                  posPan = posPan - panDegree - panDegree2;
              }
            }
            break;
          case 't': //tiltServo to be moved
            if (laptop.available()) {
              char ten = laptop.read();
              int tens = (int)ten - 48;
              char one = laptop.read();
              int ones = (int)one - 48;            
              int tiltDegree = tens*10 + ones; //Tilt angle from original position to checkpoint
              char ten2 = laptop.read();
              int tens2 = (int)ten2 - 48;
              char one2 = laptop.read();
              int ones2 = (int)one2 - 48;
              int tiltDegree2 = tens2*10 + ones2; //Tilt angle from checkpoint to end of cell
              if (rotation == 1) //clockwise rotation needed
              {
                for(i=posTilt; i<tiltDegree + tiltDegree2 + posTilt; i++)
                {
                  laptop.write('g');
                  tiltservo.write(i);
                  if (i==tiltDegree+posTilt)
                      laptop.write('t'); //Checkpoint reached. You need to send me colour instead of false now.
                    else
                      laptop.write('f'); //Ask the laptop to go straight
                  char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  if (l!='f')
                    led();
                }
                posTilt = posTilt + tiltDegree + tiltDegree2; //posTilt updated
              }
              else
              {
                for(i=posTilt; i>posTilt - tiltDegree -tiltDegree2; i--)
                {
                  laptop.write('g');
                  tiltservo.write(i);
                  if (i==tiltDegree+posTilt)
                      laptop.write('t'); //Checkpoint reached. You need to send me colour instead of false now.
                    else
                      laptop.write('f'); //Ask the laptop to go straight
                  char k = laptop.read(); //Acknowledgemnet of correct movement

                    while(!((k=='a')||(k=='z'))) //Makes sure garbage isn't being read and processed
                    {
                       
                      char p = laptop.read(); //Reads again if garbage had been read previously
                      k = p;
                    }
                    char l = laptop.read(); //checkpointColour/False will be read

                    while(!((l=='f')||(l=='r')||(l=='g')||(l=='b')||(l=='y')||(l=='w')||(l=='p')))  //Makes sure garbage isn't being read and processed
                    {
                       
                      char j = laptop.read(); //Reads again if garbage had been read previously

                      l = j;
                    }
                    if (k=='z')
                      lost();
                  if (l!='f')
                    led();
                }
                posTilt = posTilt - tiltDegree - tiltDegree2; //update posTilt
              }
            }
            break;
        }
        count ++;
      }
    } while(count<2);
  }
  laptop.write('s'); //Send next coordinates. Laptop will send 'm' or 'c' to call movee/checkpoint function and then the next set of coordinates as usual.
  return flag;  
}

/*
 * Function Name: samecell
 * Input: WiFiClient laptop
 * Output: prints samecell to laptop which is client
 * Logic: prints samecell to laptop which is client
 * Example Call: samecell();
 */ 
void samecell(WiFiClient laptop){
  laptop.write('s');
}

/*
 * Function Name: loop
 * Input: NONE
 * Output: Set initial position of servo, closes client after execution
 * Logic: Set initial position by sweeping
 *        Depending on what is sent by laptop, functions for moving, checkpoints and samecell are called and executed.
 *        When end is reached, client is disconnected.
 * Example Call: Doesn't need to be called. (First setup gets called automatically, then loop)
 */ 
void loop() {
  // listen for incoming clients
  WiFiClient laptop = server.available();
  int flag = 1;
  if (laptop) {
    Serial.println("Laptop Connected");
    //laptop.write('s'); //Send next coordinates. Laptop will send 'm' or 'c' to call movee/checkpoint function and then the next set of coordinates as usual.
    while (laptop.connected()) {
      //Serial.println("Laptop is Connected");
      if (laptop.available()) {
        //Laptop will send 'm' or 'c' or 's' to call movee/checkpoint/samecell function and then the next set of coordinates as usual.
        char c = laptop.read();
        Serial.write(c);
        if(c=='m')
           flag = movee(laptop,flag);
        if(c=='c')
        {
          flag = checkpoint(laptop, flag);
        }
        if(c=='s')
          samecell(laptop);
      }
    }
    laptop.stop();
    Serial.println("client disonnected");
  }
}
