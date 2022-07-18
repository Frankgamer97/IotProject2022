#include <WiFi.h>
#include <WiFiUdp.h>
#include <coap-simple.h>
s#include <ArduinoJson.h>

#define BAUD_RATE 9600

WiFiUDP udp;
Coap coap(udp);

char* ssid     = "TIM-Salentu";
char* password = "ScistiASantuVituETeStizzasti5724_@#";

void callback_client(CoapPacket &packet, IPAddress ip, int port){
  Serial.println("[Coap Response got]");
      
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = NULL;
      
  Serial.println(p);
}

void setup_client(){ coap.response(callback_client); }

//void setup_server(){ coap.server(callback_update,"update"); };

void callback_update(CoapPacket &packet, IPAddress ip, int port) {
  Serial.println("Receiving updates...");
      
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = NULL;
      
  //String message(p);
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, p);

  if (error) {
    Serial.print("Error during deserializzation");
    Serial.println(error.f_str());
  }
  else{
    JsonObject json  = doc.to<JsonObject>();
    if(json["min_gas"]){
      Serial.print("MIN GAS VALUE: ");
      Serial.println(json["min_gas"]);
    }
    if(json["max_gas"]){
      Serial.print("MAX GAS VALUE: ");
      Serial.print(json["max_gas"]);
    }
    if(json["frequency"]){
      Serial.print("SAMPLE FREQUENCY: ");
      Serial.println(json["frequency"]);
    }
   }
}


void update_values(float temp, float hum){
  DynamicJsonBuffer jsonBuffer;
  JsonObject &root = jsonBuffer.createObject();

  root["temp"] = temp;
  root["hum"] = hum;
  
  Serial.print("BYTE SIZE: ");
  Serial.println(sizeof(root));
 
  String output;

  root.prettyPrintTo(Serial);
  root.prettyPrintTo(output);
  coap.post(IPAddress(192, 168, 1, 30), 5683, "hello", output.c_str());
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
  setup_client();
  coap.start();
}

void loop() {
  update_values(50,30);
  delay(5000);
}
/*
if you change LED, req/res test with coap-client(libcoap), run following.
coap-client -m get coap://(arduino ip addr)/light
coap-client -e "1" -m put coap://(arduino ip addr)/light
coap-client -e "0" -m put coap://(arduino ip addr)/light
*/
