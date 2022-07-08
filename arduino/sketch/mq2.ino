#include <WiFi.h>

const char* ssid     = "****";
const char* password = "****";

#define MQ2PIN 34

void setup() {
  pinMode(MQ2PIN, INPUT);
  Serial.begin(115200);
  //WiFi.begin(ssid, password);
}

void loop() {
  int g = analogRead(MQ2PIN);

  Serial.print("Pin A0: ");
  Serial.println(g);
  delay(100);
}