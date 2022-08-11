#include "DHT.h"
#define DHTPIN 15

DHT dht(DHTPIN,DHT22);

void setup() {
  //Serial.print("Let's start");
  Serial.begin(115200);
  dht.begin();
  //Serial.print("Let's start");
  // put your setup code here, to run once:
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(1000);
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();

  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print("\n");
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.print("\n");
}
