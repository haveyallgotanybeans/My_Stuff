#define USE_TIMER1  // Force Servo to use Timer1
#include <Servo.h>
#include <NewPing.h>
// Sensor pins (Trig, Echo)
#define FRONT_CENTER_TRIG 2
#define FRONT_CENTER_ECHO 3
#define FRONT_LEFT_TRIG 4
#define FRONT_LEFT_ECHO 5
#define FRONT_RIGHT_TRIG 6
#define FRONT_RIGHT_ECHO 7
#define REAR_LEFT_TRIG 8
#define REAR_LEFT_ECHO 9
#define REAR_RIGHT_TRIG 10
#define REAR_RIGHT_ECHO 11
// Output pins
#define BUZZER 12
#define SERVO_PIN 13
#define LED_LEFT A0
#define LED_RIGHT A1
// Configuration
#define SAFETY_DISTANCE 20
#define LANE_CHANGE_DISTANCE 30
#define OBSTACLE_CONFIRM_TIME 5000
#define SERVO_LEFT 60
#define SERVO_CENTER 90
#define SERVO_RIGHT 120
#define USE_TONE false  // Set to false to avoid Timer2 conflict with NewPing
Servo laneServo;
int currentLane = 2;
unsigned long obstacleDetectedTime = 0;
bool obstacleConfirmed = false;
void setup() {
 TIMSK0 = 0;
 if (!USE_TONE) {
   TIMSK2 = 0;
 }
 pinMode(BUZZER, OUTPUT);
 pinMode(LED_LEFT, OUTPUT);
 pinMode(LED_RIGHT, OUTPUT);
 laneServo.attach(SERVO_PIN);
 laneServo.write(SERVO_CENTER);
 Serial.begin(9600);
 delay(100);
}
void loop() {
 unsigned int fcDist = getFilteredDistance(FRONT_CENTER_TRIG, FRONT_CENTER_ECHO);
 unsigned int flDist = getFilteredDistance(FRONT_LEFT_TRIG, FRONT_LEFT_ECHO);
 unsigned int frDist = getFilteredDistance(FRONT_RIGHT_TRIG, FRONT_RIGHT_ECHO);
 unsigned int rlDist = getFilteredDistance(REAR_LEFT_TRIG, REAR_LEFT_ECHO);
 unsigned int rrDist = getFilteredDistance(REAR_RIGHT_TRIG, REAR_RIGHT_ECHO);
 logSensorData(fcDist, flDist, frDist, rlDist, rrDist);
 if (fcDist > 0 && fcDist < SAFETY_DISTANCE) {
   handleObstacle(fcDist, flDist, frDist, rlDist, rrDist);
 } else {
   obstacleConfirmed = false;
   maintainLane();
 }
 delay(100);
}
unsigned int getFilteredDistance(int trigPin, int echoPin) {
 const byte samples = 3;
 unsigned int sum = 0;
 byte validReadings = 0;
 for (byte i = 0; i < samples; i++) {
   digitalWrite(trigPin, LOW);
   delayMicroseconds(2);
   digitalWrite(trigPin, HIGH);
   delayMicroseconds(10);
   digitalWrite(trigPin, LOW);
   unsigned long duration = pulseIn(echoPin, HIGH, 30000);
   if (duration > 0) {
     sum += duration * 0.034 / 2;
     validReadings++;
   }
   delay(30);
 }
 return validReadings > 0 ? sum / validReadings : 0;
}
void handleObstacle(unsigned int fc, unsigned int fl, unsigned int fr, unsigned int rl, unsigned int rr) {
 if (!obstacleConfirmed) {
   obstacleDetectedTime = millis();
   obstacleConfirmed = true;
   alertDoubleBeep();
 }
 if (millis() - obstacleDetectedTime >= OBSTACLE_CONFIRM_TIME) {
   triggerLaneChangeProtocol(fl, fr, rl, rr);
   obstacleConfirmed = false;
 }
}
void triggerLaneChangeProtocol(unsigned int fl, unsigned int fr, unsigned int rl, unsigned int rr) {
 if (currentLane > 1 && fl > LANE_CHANGE_DISTANCE && rl > LANE_CHANGE_DISTANCE) {
   changeLane(LED_LEFT, SERVO_LEFT, currentLane - 1);
 }
 else if (currentLane < 3 && fr > LANE_CHANGE_DISTANCE && rr > LANE_CHANGE_DISTANCE) {
   changeLane(LED_RIGHT, SERVO_RIGHT, currentLane + 1);
 }
 else {
   emergencyStop();
 }
}
void changeLane(int ledPin, int servoPos, int newLane) {
 digitalWrite(ledPin, HIGH);
 for (int pos = laneServo.read(); pos != servoPos; pos += (servoPos > pos) ? 1 : -1) {
   laneServo.write(pos);
   delay(15);
 }
 currentLane = newLane;
 delay(1000);
 digitalWrite(ledPin, LOW);
 alertDoubleBeep();
}
void maintainLane() {
 laneServo.write(SERVO_CENTER);
 digitalWrite(LED_LEFT, LOW);
 digitalWrite(LED_RIGHT, LOW);
}
void emergencyStop() {
 for (byte i = 0; i < 3; i++) {
   playBeep(2000, 200);
   digitalWrite(LED_LEFT, HIGH);
   digitalWrite(LED_RIGHT, HIGH);
   delay(200);
   digitalWrite(LED_LEFT, LOW);
   digitalWrite(LED_RIGHT, LOW);
   delay(200);
 }
}
void alertDoubleBeep() {
 for (byte i = 0; i < 2; i++) {
   playBeep(1500, 100);
   delay(150);
 }
}
void playBeep(int freq, int duration) {
 if (USE_TONE) {
   tone(BUZZER, freq, duration);
 } else {
   customBeep(freq, duration);
 }
}
void customBeep(int freq, int duration) {
 int period = 1000000L / freq;
 int pulse = period / 2;
 unsigned long cycles = (unsigned long)duration * 1000L / period;
 for (unsigned long i = 0; i < cycles; i++) {
   digitalWrite(BUZZER, HIGH);
   delayMicroseconds(pulse);
   digitalWrite(BUZZER, LOW);
   delayMicroseconds(pulse);
 }
}
void logSensorData(unsigned int fc, unsigned int fl, unsigned int fr, unsigned int rl, unsigned int rr) {
 Serial.print("Lane:");
 Serial.print(currentLane);
 Serial.print(" FC:");
 Serial.print(fc);
 Serial.print("cm FL:");
 Serial.print(fl);
 Serial.print("cm FR:");
 Serial.print(fr);
 Serial.print("cm RL:");
 Serial.print(rl);
 Serial.print("cm RR:");
 Serial.print(rr);
 Serial.println("cm");
}