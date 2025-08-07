#include "DFRobot_AS7341.h"

DFRobot_AS7341 as7341;
int redPin = 4;
int greenPin = 6;
int bluePin = 7;
int valvePin = 8;  

// Declare the variables here
DFRobot_AS7341::sModeOneData_t data1;
DFRobot_AS7341::sModeTwoData_t data2;
float transmittance; 

// Timing variables for valve control
unsigned long previousMillis = 0;
const long totalInterval = 45000; // Total interval of 45 seconds
const long openDuration = 1000;   // Valve open duration of 1 second

// Purge mode variables
bool purgeMode = false;
unsigned long purgeStartTime = 0;
const long purgeDuration = 10000;  // 2 minutes (120,000 milliseconds)

void setup(void) {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(valvePin, OUTPUT); 
  digitalWrite(valvePin, LOW);  // Ensure the valve is initially closed

  Serial.begin(9600);
  while (as7341.begin() != 0) {
    Serial.println("IIC init failed, please check if the wire connection is correct");
    delay(1000);
  }

  Serial.println("System ready. Type 'purge' to start purging for 2 minutes.");
}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(redPin, redValue);
  analogWrite(greenPin, greenValue);
  analogWrite(bluePin, blueValue);
}

void loop() {
  // Check for serial input
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); 
    if (command.equalsIgnoreCase("purge")) {
      purgeMode = true;
      purgeStartTime = millis();
      Serial.println("Purge mode activated. Solenoid will remain open for 2 minutes.");
      digitalWrite(valvePin, HIGH); // Open the solenoid
    }
  }

  if (purgeMode) {
    if (millis() - purgeStartTime >= purgeDuration) {
      purgeMode = false;
      digitalWrite(valvePin, LOW);
      Serial.println("Purge mode complete. Returning to normal operation.");
    } else {
      // Keep the solenoid open during purge mode
      return;
    }
  }

  // Timed valve control logic (normal operation)
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= totalInterval) {
    // Reset the timer
    previousMillis = currentMillis;

    // Open the valve for the specified duration
    digitalWrite(valvePin, HIGH);
    delay(openDuration);
    
    // Close the valve
    digitalWrite(valvePin, LOW);
  }

  // measurements
  setColor(0, 0, 255);  
  as7341.startMeasure(as7341.eF1F4ClearNIR);
  data1 = as7341.readSpectralDataOne();

  // Obtain transmittance (intensity)
  transmittance = data1.ADF1;
  Serial.println(transmittance);  // Only print intensity

  delay(500);  // Delay between readings
}
