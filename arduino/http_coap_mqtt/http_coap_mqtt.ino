/*
  Complete project details at Complete project details at https://RandomNerdTutorials.com/esp32-http-get-post-arduino/
*/

/* LIBRARIES */

#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h> //https://github.com/plapointe6/EspMQTTClient
#include <WiFiUdp.h>
#include <coap-simple.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> //v5.13.5
#include <MeanFilterLib.h> //https://github.com/luisllamasbinaburo/Arduino-Meanfilter
//#include <WifiLocation.h> //https://github.com/gmag11/WifiLocation
#include "Time.h"

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

/* PARAMETERS */
#define SERIAL_BAUD_RATE 115200
#define DHTTYPE DHT22

#define DHTPIN 15
#define MQ2PIN 34

#define AQInum 5

void callback_response(CoapPacket &packet, IPAddress ip, int port);

const char ssid[] = "RouterPi";//"TIM-Salentu";//"TIM-03859326";
const char password[] = "raspberry123";//"ScistiASantuVituETeStizzasti5724_@#";//"f5R235Dhc5bdYbCUtGfKH6zP";

/* MQTT broker configuration*/
const char* MQTT_SERVER="broker.emqx.io";
int MQTT_PORT=1883;
const char* MQTT_USER = "";
const char* MQTT_PASSWD = "";
boolean MqttConfig = false;

const char* data_topic="Iot/2022/Project/data";
const char* config_topic="Iot/2022/Project/config";


IPAddress COAP_SERVER(192, 168, 4, 1);
int COAP_PORT = 5683;
boolean Coap_Config = false;

const char* update_api = "update";
//const char* googleApiKey = "AIzaSyDfWfv8Ueu32tOjWw70PjDb1g3S3AGyo2w";
//WifiLocation location(googleApiKey);

//Your Domain name with URL path or IP address with path
const char* serverNamePost = "http://192.168.4.1:5000/update-sensor/";
const char* serverNameGet = "http://192.168.4.1:5000/get-sensor/";

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long last_sample = 0;
unsigned long sample_frequency = 3000;

float min_gas_value = 0;
float max_gas_value = 100;

float temperature = 0;
float humidity = 0;
float gas = 0;
float gps = 0;
float rssi = 0;

int protocol = 0; /* {0: http, 1: coap, 2: mqtt */

MeanFilter<float> meanFilter(AQInum);
DHT dht(DHTPIN,DHTTYPE);

PubSubClient clientMQTT;
WiFiClient clientWiFi;

WiFiUDP udp;
Coap coap(udp);

/* UTILITIES FUNCTIONS, GET AND SET PARAMETERS */

String getMonth(String month){
 if(month == "January")
  return "1";
 else if(month == "February")
  return "2";
 else if(month == "March")
  return "3";
 else if(month == "April")
  return "4";
 else if(month == "May")
  return "5";
 else if(month == "June")
  return "6";
 else if(month == "July")
  return "7";
 else if(month == "August")
  return "8";
 else if(month == "September")
  return "9";
 else if(month == "October")
  return "10";
 else if(month == "November")
  return "11";
 else if(month == "December")
  return "12";
  
 return "-1";
}

String getTime(){
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo))
    Serial.println("[NTP] Failed to obtain time");
  else{
    String now = "";
    char ts_year[5];
    char ts_month[10];
    char ts_rest[12];

    char ts_total [28];
    strftime(ts_year,sizeof(ts_year),"%Y", &timeinfo);
    //String year(ts_year);

    strftime(ts_month,sizeof(ts_month),"%B", &timeinfo);
    //String month(ts_month);

    strftime(ts_rest,sizeof(ts_rest),"%d %H %M %S", &timeinfo);
    //String rest(ts_rest);

    String year(ts_year);
    String month(ts_month);
    String rest(ts_rest);

    return year+" "+getMonth(month)+" "+rest;    
  }

  Serial.println("[NTP] Time not received");
  
  return "";
}

String getProtocol(){
  if(protocol == 0)
    return "HTTP";
  else if(protocol == 1)
    return "COAP";
  else if(protocol == 2)
    return "MQTT";
  return "HTTP" ;
}

float getGPS(int coord){
  if (coord == 0)
    return 44.083626;
  return 12.534610;
}

float getRSSI(){
  rssi = WiFi.RSSI();
  return rssi;
}

float getTemperature(){
  temperature = dht.readTemperature();
  return temperature;
}

float getHumidity(){
  humidity = dht.readHumidity();
  return humidity;
}

float getGas(){
  gas = analogRead(MQ2PIN);
  meanFilter.AddValue(gas);
  return gas;
}

int getAQI(){
  float avg = meanFilter.GetFiltered();
  
  if (avg>=max_gas_value)
    return 0;    
  else if (avg >=min_gas_value and avg< max_gas_value)
    return 1;
  else
    return 2;
}

/* CONNECTIONS */

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

void MqttConnect(){
  clientMQTT.connect("MYesp32",MQTT_USER,MQTT_PASSWD);

  int timeout = 10000;
  int intervall = 500;
  int count = 0;
  
  Serial.print("[MQTT] Connecting");
  
  while(count < timeout && !clientMQTT.connected()){
      Serial.print(".");
      count += intervall;
      delay(intervall);
  }
  
  Serial.println("");

  if(count >= timeout)
    Serial.println("[MQTT] Broker connection timeout");
  else
    Serial.println("[MQTT] Broker connection established");
}

void MqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.println("[MQTT] New message received");
  DynamicJsonBuffer jsonBuffer;
  JsonObject &root = jsonBuffer.parseObject(payload);
  if (!root.success()){
    Serial.println("[MQTT] Error parsing message");
  }
  else{
    root.prettyPrintTo(Serial);
    sample_frequency = root["sample_frequency"];
    min_gas_value = root["min_gas_value"];
    max_gas_value = root["max_gas_value"];
    protocol = root["protocol"];    
  }
}

boolean MqttPublishData(const char* topic, String value) {
  boolean conn = clientMQTT.connected();
  
  if (!conn) 
    MqttConnect();
  const char* payload=value.c_str();
  return clientMQTT.publish(topic,payload);
}

void MqttConfiguration(){
  clientMQTT.setClient(clientWiFi);
  clientMQTT.setServer(MQTT_SERVER,MQTT_PORT);
  clientMQTT.setCallback(MqttCallback);
  clientMQTT.setBufferSize(1024);
  
  MqttConnect();
  if(!clientMQTT.subscribe(config_topic))
    Serial.println("[MQTT] Error configuration");
  else{
    Serial.println("[MQTT] Connection established");
    MqttConfig=true;
  }
}

/* CoAP*/

void callback_response(CoapPacket &packet, IPAddress ip, int port){
  Serial.println("[COAP] Response got");
      
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = NULL;
      
  Serial.println(p);
}

void CoapConfiguration(){
  Coap_Config = true;
  coap.response(callback_response);
  coap.start();  
}

/* HTTP GET */

String setParametersFromServer(const char* serverName)
{
    String page = "";
    page = HTTPGet(serverName);

    DynamicJsonBuffer jsonBuffer;
    JsonObject &root = jsonBuffer.parseObject(page);
    if (!root.success()){
      Serial.println("[HTTP] Error parsing parameters json");
    }
    else{
      root.prettyPrintTo(Serial);
      sample_frequency = root["sample_frequency"];
      min_gas_value = root["min_gas_value"];
      max_gas_value = root["max_gas_value"];
      protocol = root["protocol"];
      
    }
  return page;
 
}

String HTTPGet(const char* serverName){
    String payload = "{FAILED TO CONNECT}";
    if(WiFi.status()== WL_CONNECTED){
      WiFiClient client;
      HTTPClient http;
      http.begin(client, serverName);

      int httpResponseCode = http.GET();

      if (httpResponseCode ==HTTP_CODE_OK)
      {
        payload = http.getString();
      }
      
      Serial.print("[HTTP] Response code: ");
      Serial.println(httpResponseCode);
      // Free resources
      http.end(); 
    }
    else 
    {
      Serial.println("[WiFi] Disconnected");
    }
  return payload;
}

/* HTTP POST */


String getJson()
{
        DynamicJsonBuffer jsonBuffer;
        JsonObject &root = jsonBuffer.createObject();
        JsonArray &gps_coord = root.createNestedArray("GPS");
        gps_coord.add(getGPS(0));
        gps_coord.add(getGPS(1));
        //root["GPS"] = getGPS();
        root["RSSI"] = getRSSI();
        root["Temperature"] = getTemperature();
        root["Humidity"] = getHumidity();
        root["Gas"] = getGas();
        root["AQI"] = getAQI();
        root["MAC"] = WiFi.macAddress();
        root["C_Protocol"] = getProtocol();
        root["Time"] = getTime();
        String json_str;
        root.prettyPrintTo(json_str);
        Serial.println(json_str);
        return json_str;
}

void HTTPost(const char* serverName, String json_output){
  //Send an HTTP POST request every timerDelay seconds
  
    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
        WiFiClient client;
        HTTPClient http;
        http.begin(client, serverName);
       
        // Specify content-type header
        //http.addHeader("Content-Type", "application/x-www-form-urlencoded");
        // Data to send with HTTP POST
        //String httpRequestData = "api_key=tPmAT5Ab3j7F9&sensor=BME280&value1=24.25&value2=49.54&value3=1005.14";           
        // Send HTTP POST request
        //int httpResponseCode = http.POST(httpRequestData);

        // If you need an HTTP request with a content type: text/plain
        //http.addHeader("Content-Type", "text/plain");
        //int httpResponseCode = http.POST("Hello, World!");
             
        // If you need an HTTP request with a content type: application/json, use the following:
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode = http.POST(json_output);

        Serial.print("[HTTP] Response code: ");
        Serial.println(httpResponseCode);
          
        // Free resources
        http.end();   
    }
    else {
      Serial.println("[WiFi] Disconnected");
    } 
}

/* ESP32 WORK-FLOW */

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  dht.begin();
  pinMode(MQ2PIN,INPUT);
  WifiConnection();
  if(protocol == 2)
    MqttConfiguration();
  else if(protocol == 1)
    CoapConfiguration();

  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

void loop() {

  if ((millis() - last_sample) > sample_frequency) {
    Serial.println();
    Serial.println("======================");
    Serial.print("Timer set to ");
    Serial.println(sample_frequency);

      if (protocol==0)
      {
	      Serial.println();
	      Serial.println("Using HTTP");
        String page = "";
        page = setParametersFromServer(serverNameGet);
        HTTPost(serverNamePost,getJson());
      }
      else if (protocol==1)
      {
	      String page = "";
        page = setParametersFromServer(serverNameGet);
        
	      Serial.println();
        Serial.println("Using CoAP");
        
        if(!Coap_Config)
          CoapConfiguration();
       
        coap.put(COAP_SERVER, COAP_PORT, update_api, getJson().c_str());
      }      
      else if (protocol==2)
      {
	      Serial.println();
        Serial.println("Using Mqtt");
        if(!MqttConfig)
          MqttConfiguration();
        
        boolean published_data = MqttPublishData(data_topic,getJson());
        Serial.print("[MQTT] Data published: ");
        Serial.println(published_data);
      }
      
      last_sample = millis();
  }
  if(protocol == 1)
    coap.loop();
  else if(protocol == 2)
    clientMQTT.loop();
}
