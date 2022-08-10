#include <Wire.h>
#include <TinyGPS++.h>
#include <WiFi.h>

#define RXD2 16
#define TXD2 17
HardwareSerial neogps(1);

const char ssid[] = "JeepMobile";//"TIM-Salentu";//"RouterPi";//"TIM-03859326";
const char password[] = "@dQmBvxoNRiINTG@1LxZ5JshRz@";//"ScistiASantuVituETeStizzasti5724_@#";//"raspberry123";//"f5R235Dhc5bdYbCUtGfKH6zP";

TinyGPSPlus gps;


void WifiConnection(){
  WiFi.begin(ssid, password);
  Serial.print("[WiFi] Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("[WiFi] Connection Established");
  Serial.print("[WiFi] Ip address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  //Begin serial communication Arduino IDE (Serial Monitor)
  WifiConnection();
  //Begin serial communication Neo6mGPS
  neogps.begin(9600, SERIAL_8N1, RXD2, TXD2);
}

void loop() {
    
  boolean newData = false;
  for (unsigned long start = millis(); millis() - start < 1000;)
  {
    while (neogps.available())
    {
      if (gps.encode(neogps.read()))
      {
        newData = true;
      }
    }
  }

  //If newData is true
  if(newData == true)
  {
    newData = false;
    Serial.println(gps.satellites.value());
    print_speed();
  }
  else
    Serial.println("[LOOP] NO DATA");
}

void print_speed()
{
  if (gps.location.isValid() == 1)
  {   
    Serial.println(gps.location.lat(),6);
    Serial.println(gps.location.lng(),6);
    Serial.print(gps.speed.kmph());
    Serial.print(gps.satellites.value());
    Serial.print(gps.altitude.meters());
  }
  else
    Serial.println("[PRINT] No Data");  

}
