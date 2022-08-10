// This example uses an ESP32 Development Board
// to connect to shiftr.io.
//
// You can check on your device after a successful
// connection here: https://www.shiftr.io/try.
//
// by Joël Gähwiler
// https://github.com/256dpi/arduino-mqtt

#include <WiFiMulti.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char ssid[] = "TIM-03859326";
const char pass[] = "f5R235Dhc5bdYbCUtGfKH6zP";

WiFiMulti wmulti;


void setup() {
  Serial.begin(115200);
  wmulti.addAP(ssid, pass);
  Serial.println("Ready...");
}


void getPage(){
  if (wmulti.run()==WL_CONNECTED){
    HTTPClient http;
    http.begin("http://www.zeppelinmaker.it/helloworld.txt");

    int httpcode = http.GET();
    //Serial.print("HTTP code:");
    //Serial.println(httpcode);

    if (httpcode>0){
      if (httpcode==HTTP_CODE_OK){
        String page = http.getString();
        Serial.println("=============================");
        Serial.println(page);
        Serial.println("=============================");
      }

    }else{
    //  Serial.println("HTTP failed");
    //  Serial.println(http.errorToString(httpcode).c_str());
    }

    http.end();
  }

}

void loop() {
  delay(2000);
  // Serial.println(Serial.available());
  //while(Serial.available()){
  //  Serial.println("here");
  //  char ch = Serial.read();
  //  if (ch == 's') {
      getPage();
   // }
   // else{
   //   Serial.println("char not found");
   //   Serial.println(ch);}

  //}
  //    delay(5000);
}
