// #include <INST.h>
// #include <SCS.h>
// #include <SCSCL.h>
// #include <SCSerail.h>
// #include <SCServo.h>
// #include <SMSBL.h>
// #include <SMSCL.h>
#include <math.h>
#include <SCServo.h>



#define motorNum 2    //Number of motors
u8 mID[motorNum] = {1,2};
volatile s16 posTarget[motorNum] = {};
volatile s16 timeTarget[motorNum] = {};
volatile bool bMove;


//Global Var
SCSCL sc;
long int mBaudrate = 1000000;
long int sBaudrate = 1000000;


volatile int modeInt;
String inputStr = "";
volatile unsigned long millis_now[2], elapsetime[2], Moving[2];
volatile bool MoveTrig[2];


void setup() {
  Serial.begin(sBaudrate, SERIAL_8N1);
  while(!Serial);
  Serial2.begin(mBaudrate);
  while(!Serial2);
  sc.pSerial = &Serial2;
  inputStr.reserve(200);
  modeInt = 0;
  bMove = false;
  for(int i = 0; i < motorNum; i++){
    MoveTrig[i] = false;
  }
}

void loop() {

  //Read String if Serial available
  if(Serial.available()){
    inputStr = Serial.readStringUntil('\n'); //Read the serial command till newline character
    inputStr.trim();
  }
  
  //Process the string to update posTarget and timeTarget
  if(inputStr != ""){ //Expected input: "pos1,pos2;spd1,spd2\n"

    int semicolIndex; //Index for the 1 semicolon expected in inputStr
    int commaIndex[2] = {}; //Index for the 2 commas expected in inputStr
    int count_comma = 0; //Counter for commas

    //Find the position of the semicolon and comma
    for (int i = 0; i < inputStr.length() - 1; i++){
      if(inputStr[i] == ';'){
        semicolIndex = i;
      }
      if(inputStr[i] == ','){
        commaIndex[count_comma] = i;
        count_comma += 1;
      }
    }
    count_comma = 0; //Reset counter for next incoming command

    //Cut inputStr and update posTarget and timeTarget
    posTarget[0] = cutStr(inputStr, 0, commaIndex[0]-1).toInt();
    posTarget[1] = cutStr(inputStr, commaIndex[0]+1, semicolIndex-1).toInt();
    timeTarget[0] = cutStr(inputStr, semicolIndex+1, commaIndex[1]-1).toInt();
    timeTarget[1] = cutStr(inputStr, commaIndex[1]+1, inputStr.length()-1).toInt();
    
    // Serial.print(posTarget[0]); Serial.print(", "); Serial.print(posTarget[1]); Serial.print("; "); Serial.print(timeTarget[0]); Serial.print(", "); Serial.println(timeTarget[1]);

    modeInt = 1; //Switch to moving mode
    bMove = true;
    for(int i = 0; i < motorNum; i++){
      MoveTrig[i] = true;
    }
    // Serial.println("Case 1 bMove = true");
    inputStr = ""; //Clear inputStr
  }

  // Serial.println(bMove);
  // Serial.print(",");
  // Serial.println(mMoving());
  bool bMoving = mMoving();
  // Serial.print("Moving: "); Serial.println(bMoving);
  // Serial.print(Moving[0]); Serial.print(", "); Serial.println(Moving[1]);

  switch(modeInt){
    
    case 0: //Idle Mode
      // if(bMoving){
      //   Serial.println("Moving");
      // }
      if(bMove){
        for(int i = 0; i < motorNum; i++){
          if(MoveTrig[i] and !(Moving[i])){
            // Serial.print("Motor "); Serial.print(i); Serial.println("finished motion");
            elapsetime[i] = millis() - millis_now[i];
            MoveTrig[i] = false;
          }
        }
        if(!(bMoving)){
          Serial.print(elapsetime[0]); Serial.print(","); Serial.println(elapsetime[1]);
          bMove = false;
        }
      }
    break;                      

    case 1: //RegWritePos mode
      for(int i = 0; i < motorNum; i++){
        sc.RegWritePos(mID[i], posTarget[i], timeTarget[i], 0);
      }
      sc.RegWriteAction();
      millis_now[0] = millis();
      millis_now[1] = millis_now[0]; //Collect timestamp when actuated
      modeInt = 0;
      delay(5);
      // Serial.println("Act");
    break;
  }

}


String cutStr(String inputStr, int start, int end){
  //Function for cuting inputStr from start to end (include start and end char)
  String tmpStr = "";
  tmpStr.reserve(200);
  for (int i = start; i < end+1; i++){
    if(inputStr[i] != ' '){
      tmpStr += inputStr[i];
    }
  }
  return tmpStr;
}

bool mMoving(){
  //Check if the motoring moving in current loop
  bool b_Moving = false;
  for(int i = 0; i < motorNum; i++){
    if(sc.ReadMove(mID[i]) != 0){
      Moving[i] = true;
      b_Moving = true;
    }
    else {
      Moving[i] = false;
    }
  }
  return b_Moving;
}



//Comments blocking Arduino IDE Code Eating behaviour