#include <Servo.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>

// Motor pins
const int ENA = 9;
const int IN1 = 8;
const int IN2 = 7;
const int IN3 = 6;
const int IN4 = 5;
const int ENB = 3;

// Sensor pins
const int trigPin = A0;
const int echoPin = A1;

// Servo objects
Servo radarServo;
Servo thermalServo;

// Thermal sensor
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// Variables
int radarAngle = 90;  // Center position
int thermalAngle = 90;
bool scanning = true;
bool humanDetected = false;
int scanDirection = 1;  // 1 for right, -1 for left

// Human temperature range (Celsius)
const float MIN_HUMAN_TEMP = 30.0;
const float MAX_HUMAN_TEMP = 40.0;

void setup() {
  Serial.begin(9600);
  
  // Initialize motor pins
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  // Initialize ultrasonic
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  // Initialize servos
  radarServo.attach(10);
  thermalServo.attach(11);
  
  // Initialize thermal sensor
  if (!mlx.begin()) {
    Serial.println("MLX90614 not found!");
    while (1);
  }
  
  // Center servos
  radarServo.write(90);
  thermalServo.write(90);
  delay(1000);
  
  Serial.println("Search and Rescue Robot Ready!");
}

void loop() {
  if (humanDetected) {
    // Human detected - stop everything
    stopRobot();
    scanning = false;
    Serial.println("HUMAN DETECTED - MISSION ACCOMPLISHED");
    delay(1000);
    return;
  }
  
  // Scan environment
  scanEnvironment();
  
  // Check for obstacles and navigate
  navigate();
  
  // Move forward slowly
  moveForward(150);
}

void scanEnvironment() {
  // Move radar servo (scan from 30 to 150 degrees)
  radarAngle += (5 * scanDirection);
  radarServo.write(radarAngle);
  
  // Move thermal servo in opposite direction for wider coverage
  thermalAngle -= (5 * scanDirection);
  thermalServo.write(thermalAngle);
  
  // Change direction at limits
  if (radarAngle >= 150 || radarAngle <= 30) {
    scanDirection *= -1;
  }
  
  // Read thermal sensor
  float ambientTemp = mlx.readAmbientTempC();
  float objectTemp = mlx.readObjectTempC();
  
  Serial.print("Ambient: "); Serial.print(ambientTemp);
  Serial.print("C | Object: "); Serial.print(objectTemp);
  Serial.print("C | Radar Angle: "); Serial.println(radarAngle);
  
  // Check for human temperature
  if (objectTemp >= MIN_HUMAN_TEMP && objectTemp <= MAX_HUMAN_TEMP) {
    humanDetected = true;
    Serial.println("*** HUMAN TEMPERATURE DETECTED ***");
  }
  
  delay(100);
}

void navigate() {
  long distance = getDistance();
  
  Serial.print("Distance: "); Serial.println(distance);
  
  // Obstacle avoidance
  if (distance < 20) {
    avoidObstacle();
  }
}

long getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH);
  long distance = duration * 0.034 / 2;
  
  return distance;
}

void avoidObstacle() {
  Serial.println("Obstacle detected! Avoiding...");
  
  stopRobot();
  delay(500);
  
  // Check right side
  radarServo.write(0);
  delay(500);
  long rightDist = getDistance();
  
  // Check left side
  radarServo.write(180);
  delay(500);
  long leftDist = getDistance();
  
  // Return to center
  radarServo.write(90);
  delay(500);
  
  // Decide direction
  if (rightDist > leftDist && rightDist > 25) {
    // Turn right
    turnRight(200);
    delay(300);
  } else if (leftDist > 25) {
    // Turn left
    turnLeft(200);
    delay(300);
  } else {
    // Turn around
    turnRight(200);
    delay(600);
  }
}

// Motor control functions
void moveForward(int speed) {
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void stopRobot() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void turnRight(int speed) {
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnLeft(int speed) {
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}