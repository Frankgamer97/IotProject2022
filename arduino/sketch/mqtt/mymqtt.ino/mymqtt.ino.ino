#include "WiFi.h"
#include <PubSubClient.h>
#include <DHT.h>

#define PIN_DHT 15
#define DEFAULT_SENSE_FREQUENCY 10000
#define SERIAL_BAUD_RATE 9600

char* SSID     = "TIM-Salentu";
char* PASS = "ScistiASantuVituETeStizzasti5724_@#";

const char* MQTT_SERVER="broker.emqx.io";
int MQTT_PORT=1883;
const char* MQTT_USER = "";
const char* MQTT_PASSWD = "";
boolean resultMQTT = false;

const char* temp_topic="iotProject2022/temp";
const char* hum_topic="iotProject2022/hum";
const char* config_topic="iotProject2022/config";

DHT dht(PIN_DHT, DHT22);
PubSubClient clientMQTT; 
WiFiClient clientWiFi;

float tempValue;
float humValue;

void connect() {
  WiFi.begin(SSID, PASS);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connection attempt");
    delay(500);
  }
  Serial.println("WiFi connected");
  Serial.println(WiFi.localIP());
  delay(5000);
}

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  dht.begin();
  connect();
  clientMQTT.setClient(clientWiFi);
  clientMQTT.setServer(MQTT_SERVER,MQTT_PORT);
  clientMQTT.setCallback(callback);
  clientMQTT.setBufferSize(400);
  resultMQTT=false;

  MQTT_connect();
  clientMQTT.subscribe(config_topic);
}

void MQTT_connect(){
  clientMQTT.connect("MYesp32",MQTT_USER,MQTT_PASSWD);
  while(!clientMQTT.connected());
  Serial.println("[ESTABLISHED] MQTT broker connection");
  
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

boolean publishData(const char* topic, float value) {
  
  if (!clientMQTT.connected()) 
    MQTT_connect();

  String message=String(value);
  const char* payload=message.c_str();
  return clientMQTT.publish(topic,payload);
}

void loop() {
  
  /*tempValue=dht.readTemperature();
  Serial.println(tempValue);
  resultMQTT=publishData(temp_topic,tempValue);

  humValue=dht.readHumidity();
  Serial.println(humValue);
  resultMQTT=publishData(hum_topic,humValue);*/
  clientMQTT.loop();
  delay(DEFAULT_SENSE_FREQUENCY);
  
}
