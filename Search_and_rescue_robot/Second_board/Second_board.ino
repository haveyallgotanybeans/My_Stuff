#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>

// Assign a unique ID to the accelerometer
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

// Buzzer pin
const int buzzerPin = 9;

// Variables
float currentZ = 0;
float previousZ = 0;
unsigned long toppleStartTime = 0;
unsigned long stationaryStartTime = 0;
bool isToppled = false;
bool isStationary = false;
bool humanAlertActive = false;
bool toppleAlertActive = false;

// Timing constants
const unsigned long TOPPLE_TIME_THRESHOLD = 5000;    // 5 seconds
const unsigned long STATIONARY_TIME_THRESHOLD = 10000; // 10 seconds
const float MOVEMENT_THRESHOLD = 0.5;               // Acceleration change threshold

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
  
  // Initialize accelerometer
  if (!accel.begin()) {
    Serial.println("ADXL345 not found!");
    while (1);
  }
  
  accel.setRange(ADXL345_RANGE_16_G);
  Serial.println("Safety Monitor Ready!");
}

void loop() {
  // Get accelerometer data
  sensors_event_t event;
  accel.getEvent(&event);
  currentZ = event.acceleration.z;
  
  // Check for toppling (robot upside down)
  checkToppling();
  
  // Check for stationary condition (human detected)
  checkStationary();
  
  // Control buzzer alerts
  controlAlerts();
  
  previousZ = currentZ;
  delay(100);
}

void checkToppling() {
  // If Z axis is negative (upside down) and wasn't previously toppled
  if (currentZ < -1.0 && !isToppled) {
    if (toppleStartTime == 0) {
      toppleStartTime = millis();
    } else if (millis() - toppleStartTime > TOPPLE_TIME_THRESHOLD) {
      isToppled = true;
      toppleAlertActive = true;
      Serial.println("ROBOT TOPPLED! Sending high-frequency alert.");
    }
  } 
  // If robot is upright again
  else if (currentZ > 1.0 && isToppled) {
    isToppled = false;
    toppleStartTime = 0;
    toppleAlertActive = false;
    Serial.println("Robot upright again.");
  }
}

void checkStationary() {
  // Calculate movement (change in acceleration)
  float movement = abs(currentZ - previousZ);
  
  // If little movement detected
  if (movement < MOVEMENT_THRESHOLD && !isStationary) {
    if (stationaryStartTime == 0) {
      stationaryStartTime = millis();
    } else if (millis() - stationaryStartTime > STATIONARY_TIME_THRESHOLD) {
      isStationary = true;
      humanAlertActive = true;
      Serial.println("ROBOT STATIONARY - HUMAN DETECTED! Sending continuous alert.");
    }
  } 
  // If movement detected again
  else if (movement >= MOVEMENT_THRESHOLD && isStationary) {
    isStationary = false;
    stationaryStartTime = 0;
    humanAlertActive = false;
    Serial.println("Robot moving again.");
  }
}

void controlAlerts() {
  if (toppleAlertActive) {
    // High frequency alert for toppling (beep beep beep)
    tone(buzzerPin, 2000, 200);
    delay(200);
    noTone(buzzerPin);
    delay(100);
  } 
  else if (humanAlertActive) {
    // Continuous alert for human detected
    tone(buzzerPin, 1000);
  } 
  else {
    // No alerts
    noTone(buzzerPin);
  }
}

void printAcceleration() {
  Serial.print("Z: "); Serial.print(currentZ);
  Serial.print(" | Toppled: "); Serial.print(isToppled);
  Serial.print(" | Stationary: "); Serial.print(isStationary);
  Serial.print(" | Human Alert: "); Serial.print(humanAlertActive);
  Serial.print(" | Topple Alert: "); Serial.println(toppleAlertActive);
}