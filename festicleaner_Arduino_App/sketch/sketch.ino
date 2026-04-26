#include <Arduino.h>
#include <Arduino_RouterBridge.h> // Required to talk to Python
#include <Arduino_Modulino.h>     // NEW: Required for the plug-and-play sensors

ModulinoDistance distSensor;
ModulinoThermo thermoSensor;

// DC MOTORS
int PwmRight = 10;
int MotorRightForward = 4;
int MotorRightBack = 8;

int PwmLeft = 5;
int MotorLeftForward = 6;
int MotorLeftBack = 7;

// SERVOS
int servoRight = 3;
int servoLeft = 2;

// Computer Vision math
const int FRAME_WIDTH = 640;
const int FRAME_HEIGHT = 520;
const int CENTER_X = FRAME_WIDTH / 2;
const int CENTER_Y = FRAME_HEIGHT / 2;
const int DEADZONE = 30; // Ignore small errors to prevent jitter
const int GRAB_THRESHOLD = 250; // 
const int HOME_THRESHOLD = 250; // Y-coordinate indicating home is close enough
const int CLOSE_THRESHOLD = 300;

// Testing variables
int step_num = 0;
int last_printed_step = -1;

// Tracking Variables updated by Python
volatile int object_type = 0; // 0 = nothing, 1 = cup/bottle, 2 = cell phone (home)
volatile int targetX = -1;
volatile int targetY = -1;
volatile unsigned long lastDetectionTime = 0;
volatile bool isPoweredOn = true; 

// ---------------------------------------------------------
// MOTOR & SERVO FUNCTIONS
// ---------------------------------------------------------
void moveForward(int speed) {
  analogWrite(PwmRight, speed);
  analogWrite(PwmLeft, speed);
  digitalWrite(MotorRightForward, HIGH);
  digitalWrite(MotorRightBack, LOW);
  digitalWrite(MotorLeftForward, HIGH);
  digitalWrite(MotorLeftBack, LOW); 
}

void moveBackwards(int speed) {
  analogWrite(PwmRight, speed);
  analogWrite(PwmLeft, speed);
  digitalWrite(MotorRightForward, LOW);
  digitalWrite(MotorRightBack, HIGH);
  digitalWrite(MotorLeftForward, LOW);
  digitalWrite(MotorLeftBack, HIGH);
}

void turnRight(int speed) {
  analogWrite(PwmRight, speed);
  analogWrite(PwmLeft, speed);
  digitalWrite(MotorRightForward, HIGH);
  digitalWrite(MotorRightBack, LOW);
  digitalWrite(MotorLeftForward, LOW);
  digitalWrite(MotorLeftBack, HIGH);
}

void turnLeft(int speed) {
  analogWrite(PwmRight, speed);
  analogWrite(PwmLeft, speed);
  digitalWrite(MotorRightForward, LOW);
  digitalWrite(MotorRightBack, HIGH);
  digitalWrite(MotorLeftForward, HIGH);
  digitalWrite(MotorLeftBack, LOW);
}

void stopMotors() {
  digitalWrite(MotorRightForward, LOW);
  digitalWrite(MotorRightBack, LOW);
  digitalWrite(MotorLeftForward, LOW);
  digitalWrite(MotorLeftBack, LOW);
}

void moveServo(int pin_in, int angle) {
  angle = constrain(angle, 0, 180);
  int pulseWidth = map(angle, 0, 180, 1000, 2000);
  digitalWrite(pin_in, HIGH);
  delayMicroseconds(pulseWidth);
  digitalWrite(pin_in, LOW);
}

void openGripper() {
  for (int i = 0; i < 50; i++) { 
    moveServo(servoRight, 90);
    moveServo(servoLeft, 0);
    delay(18); 
  }
}

void closeGripper() {
  for (int i = 0; i < 50; i++) { 
    moveServo(servoRight, 30);
    moveServo(servoLeft, 40);
    delay(18); 
  }
}

void trackObject(int x, int y) {
  int xError = x - CENTER_X;
  //float dist = current_dist_mm;
  
  // 1. ORIENTATION (X-axis)
  if (abs(xError) > DEADZONE) {
    int turnDuration = map(abs(xError), 0, CENTER_X, 50, 400);
    int turnSpeed = 200;
    int speed = 200;
    
    if (xError > 0) {
      // Object is on the right -> Turn Right
      turnRight(turnSpeed);
      delay(turnDuration); // Give it a moment to turn
      stopMotors();
      delay(800);
      moveForward(speed); 
      delay(200);
      stopMotors();
      delay(400);
    } else {
      // Object is on the left -> Turn Left
      turnLeft(turnSpeed);
      delay(turnDuration); // Give it a moment to turn
      stopMotors();
      delay(800);
      moveForward(speed); 
      delay(200);
      stopMotors();
      delay(400);
    }
  } else {
    // If it is centered, just drive straight
    moveForward(200);
    delay(200);
    stopMotors();
    delay(800);
  }
}

// ---------------------------------------------------------
// BRIDGE COMMUNICATION
// ---------------------------------------------------------
// This function fires automatically when Python calls "updateTarget"
void onUpdateTarget(int id, int x, int y) {
  object_type = id; // 1 for target, 2 for home
  targetX = x;
  targetY = y;
  lastDetectionTime = millis();

  /*
  object_type = Bridge.getInt(); // 1 for target, 2 for home
  targetX = Bridge.getInt();
  targetY = Bridge.getInt();
  lastDetectionTime = millis();
  */
  
  // --- DEBUG PRINT ---
  /*
  Serial.print("BRIDGE RCVD -> ID: ");
  Serial.print(object_type);
  Serial.print(" | X: ");
  Serial.print(targetX);
  Serial.print(" | Y: ");
  Serial.println(targetY);
  */
}

void setPowerState(int state) {
  if (state == 1) {
    isPoweredOn = true;
  } else {
    isPoweredOn = false;
    // IMMEDIATE KILL SWITCH & RESET
    stopMotors();
    openGripper();
    
    // Reset all tracking variables
    step_num = 0; 
    object_type = 0;
    targetX = -1;
    targetY = -1;
  }
}
// ---------------------------------------------------------
// SETUP & MAIN LOOP
// ---------------------------------------------------------
void setup() {
  Serial.begin(9600);

  // Define motor pins
  pinMode(PwmRight, OUTPUT);
  pinMode(PwmLeft, OUTPUT);
  pinMode(MotorRightForward, OUTPUT);
  pinMode(MotorRightBack, OUTPUT);
  pinMode(MotorLeftForward, OUTPUT);
  pinMode(MotorLeftBack, OUTPUT);
  
  // Define servo pins
  pinMode(servoRight, OUTPUT);
  pinMode(servoLeft, OUTPUT);

  // Start the Bridge and register the Python listener
  Bridge.begin();
  Bridge.provide("updateTarget", onUpdateTarget);
  Bridge.provide("setPowerState", setPowerState);

  Modulino.begin();
  distSensor.begin();
  thermoSensor.begin();
  
  

  stopMotors(); 
  openGripper(); 

  step_num = 0;
}

void loop() {
  // Keep the bridge alive to listen for Python messages
  //Bridge.poll(); 
  if (!isPoweredOn) {
    return; 
  }
  static unsigned long lastThermoRead = 0;
  if (millis() - lastThermoRead > 5000) {
    lastThermoRead = millis(); // Reset the timer
    float temp = thermoSensor.getTemperature();
    float humidity = thermoSensor.getHumidity();

    if (!isnan(temp)) {
          Bridge.call("tempSensor", temp);
    }
    if (!isnan(humidity)) { 
          Bridge.call("humiditySensor", humidity);
    }
  }
  if (distSensor.available()) {
    float current_dist = distSensor.get();
    if (!isnan(current_dist)) {
      Bridge.call("distanceTraget", current_dist);  
    }
  }
  
  // --- DEBUG PRINT FOR STEPS ---
  if (step_num != last_printed_step) {
    // Send the step number over the Wi-Fi Bridge to Python!
    Bridge.call("logStep", step_num);
    last_printed_step = step_num;
  }
  // -----------------------------

  // --- DATA STATE CHECK ---
  // If we haven't seen an object in 2 seconds, clear the variables so the robot knows it's lost.
  bool hasRecentData = (millis() - lastDetectionTime < 2000);
  if (!hasRecentData) {
    object_type = 0;
    targetX = -1;
    targetY = -1;
  }

  // ------ Step 0: Initialization -------
  if (step_num == 0){
    stopMotors(); 
    openGripper(); 
    delay(200);
    step_num = 1;
  }

  // ------ Step 1: Look for Objects -------
  else if (step_num == 1){
    //wait until we get some object information
    if (object_type != 1){ 
      // If we don't see a cup/bottle yet
      //spin 10º 
      int turnSpeed = 200;
      turnRight(turnSpeed);
      delay(300);
      stopMotors();
      delay(800);
    }
    else {
      step_num = 2;
    }
  }
  
  // ------ Step 2: Go To Objects -------
  else if (step_num == 2){
    if (distSensor.available()) {
      float current_dist = distSensor.get();
      if ((GRAB_THRESHOLD < current_dist)&&(current_dist < CLOSE_THRESHOLD)){
        // Object is still far away, keep tracking
        moveForward(200);
        delay(200);
        stopMotors();
        delay(800);
        trackObject(targetX, targetY);
        
      }
      
      if (current_dist < GRAB_THRESHOLD){
          stopMotors();
          delay(500);
          closeGripper();
          // Clear the target so we don't immediately try to grab it again
          targetX = -1;
          targetY = -1;
          object_type = 0;
  
          // Go to next step
          step_num = 3; 
        }  
    }
    // if we have an active target 
    if (object_type == 1) {
      // Read and Print distance
      if (distSensor.available()) {
        float current_dist = distSensor.get();
        
        // If the object is too far away, it returns NaN (Not a Number), so we filter that out
        if (!isnan(current_dist)) {
          // --- DEBUG PRINT FOR STEPS ---
          Bridge.call("distanceTraget", current_dist);
        }
        if (current_dist < GRAB_THRESHOLD){
          stopMotors();
          delay(500);
          closeGripper();
          // Clear the target so we don't immediately try to grab it again
          targetX = -1;
          targetY = -1;
          object_type = 0;
  
          // Go to next step
          step_num = 3; 
        } 
        else {
          // Object is still far away, keep tracking
          trackObject(targetX, targetY);
        }
      } else {
        // Object is still far away, keep tracking
          trackObject(targetX, targetY);
      }
    }
  }
  
  // ------ Step 3: Bring Object Home -------
  else if (step_num == 3){
    //bring object home logic
    if (object_type != 2) { // If we don't see the cell phone (home) yet
      //spin 10º -> until we see the object that signals home (object_type == "cell phone")
      int turnSpeed = 200;
      turnRight(turnSpeed);
      delay(600);
      stopMotors();
      delay(500);
    }
    else {
      if (distSensor.available()) {
        float current_dist = distSensor.get();
        if (!isnan(current_dist)) {
          // --- DEBUG PRINT FOR STEPS ---
          Bridge.call("distanceTraget", current_dist); 
        }
        // We see home! 
        if (current_dist < HOME_THRESHOLD) {
          stopMotors();
          delay(500);
          step_num = 4; 
        } 
        else {
          trackObject(targetX, targetY);
        }
      }
    }
  }
  
  // ------ Step 4: Finish -------
  else if (step_num == 4){
    stopMotors(); 
    // drop object
    openGripper(); 
    delay(500);

    // move away a bit
    int speed = 200;
    moveBackwards(speed);
    delay(1000);
    stopMotors();

    step_num = 5; // stop forever
  }
}