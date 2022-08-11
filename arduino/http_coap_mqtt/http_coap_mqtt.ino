
/* LIBRARIES */
#include <Wire.h>
#include <TinyGPS++.h> //https://github.com/mikalhart/TinyGPSPlus//v1.0.3
#include <LiquidCrystal_I2C.h> //https://github.com/fdebrabander/Arduino-LiquidCrystal-I2C-library//last version
#include <DHT.h> //https://github.com/adafruit/DHT-sensor-library//v1.4.4
#include <WiFi.h>
#include <PubSubClient.h> //https://github.com/plapointe6/EspMQTTClient//v1.13.3
#include <WiFiUdp.h>
#include <coap-simple.h> //https://github.com/hirotakaster/CoAP-simple-library//v1.3.24
#include <HTTPClient.h>
#include <ArduinoJson.h> //https://github.com/bblanchon/ArduinoJson//v5.13.5
#include <MeanFilterLib.h> //https://github.com/luisllamasbinaburo/Arduino-Meanfilter//v1.0.0
#include "Time.h"

/* DEFINE */
#define SERIAL_BAUD_RATE 115200
#define DHTTYPE DHT22

#define RXD2 16
#define TXD2 17
#define GPS_TIMEOUT 10000
#define DHTPIN 15
#define MQ2PIN 34

#define AQInum 5

/* PARAMETERS */
String user_id = "";

const char ssid[] = "22lr";
const char password[] = "raspberry123";

String protocol = "HTTP"; /* HTTP,COAP, MQTT */

/* HTTP parameters*/
//Your Domain name with URL path or IP address with path
const char* serverNamePost = "http://192.168.4.1:5000/update-sensor/";
const char* serverNameGet = "http://192.168.4.1:5000/get-sensor/";
/* */


/* COAP parameters*/
IPAddress COAP_SERVER(192, 168, 4, 1);
int COAP_PORT = 5683;
boolean Coap_Config = false;
const char* update_api = "update";
void callback_response(CoapPacket &packet, IPAddress ip, int port);

WiFiUDP udp;
Coap coap(udp);
/* */


/* MQTT broker parameters*/
const char* MQTT_SERVER="broker.emqx.io";
int MQTT_PORT=1883;
const char* MQTT_USER = "";
const char* MQTT_PASSWD = "";
boolean MqttConfig = false;

const char* data_topic="Iot/2022/Project/data";
const char* config_topic="Iot/2022/Project/config";

PubSubClient clientMQTT;
WiFiClient clientWiFi;
/* */

/* NTP parameters*/
const char* ntpServer = "uk.pool.ntp.org";
const long  gmtOffset_sec = 0;//3600;
const int   daylightOffset_sec = 0;//3600;
/* */

/* GPS parameters*/
float GPS_LAT = 44.488;
float GPS_LNG = 11.330;
HardwareSerial neogps(1);
TinyGPSPlus gps;
/* */

/* PDR parameters*/
int http_total_packets = 0;
int http_sent_packets = 0;

int coap_total_packets = 0;
int coap_sent_packets = 0;

int mqtt_total_packets = 0;
int mqtt_sent_packets = 0;
/* */


LiquidCrystal_I2C lcd(0x27, 16,2);



/* sensory parameters*/
// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long last_sample = 0;
unsigned long sample_frequency = 5000;

float min_gas_value = 0;
float max_gas_value = 100;

float temperature = 0;
float humidity = 0;
float gas = 0;
//float gps = 0;
float rssi = 0;


MeanFilter<float> meanFilter(AQInum);
DHT dht(DHTPIN,DHTTYPE);
/* */



/* UTILITIES FUNCTIONS, GET AND SET PARAMETERS */

/* NTP functions*/
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
/* */

String getProtocol(){
  /*if(protocol == 0)
    return "HTTP";
  else if(protocol == 1)
    return "COAP";
  else if(protocol == 2)
    return "MQTT";
  return "HTTP" ;*/
  return protocol;
}

/* sensory functions */

float getPDR(){
  if(protocol == String("HTTP"))
    return http_sent_packets >= 0 && http_total_packets > 0?((float)http_sent_packets) / http_total_packets:0 ;
  if(protocol == String("COAP"))
    return coap_sent_packets >= 0 && coap_total_packets > 0?((float)coap_sent_packets) / coap_total_packets:0;
  if(protocol == String("MQTT"))
    return mqtt_sent_packets >= 0 && mqtt_total_packets > 0?((float)mqtt_sent_packets) / mqtt_total_packets:0;

  return -1;
}

float myround(float num, int places){
  return String(num,places).toFloat();
}

void updateGPS(){
  boolean new_data = false;
  unsigned long start_while = millis();
  
  while (neogps.available() && start_while - millis() < GPS_TIMEOUT){
      if (gps.encode(neogps.read())){
        new_data = true;
        break;
      }
  }
  
  if(new_data == true){
    if(gps.location.isValid() == 1){
      GPS_LAT = myround(gps.location.lat(),3);
      GPS_LNG = myround(gps.location.lng(),3);
      //GPS_LAT = gps.location.lat();
      //GPS_LNG = gps.location.lng();

      /*
      lcd.clear();
      lcd.setCursor(0,1);
      lcd.print(GPS_LAT, 3);
      lcd.print("   ");
      lcd.print(GPS_LNG, 3);  
      */
    }
    else
      Serial.println("[GPS] NO VALID DATA");
  }
  else
    Serial.println("[GPS] NO DATA");
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
/* */

/* LCD DISPLAY functions*/
void  DisplayConfiguration () {
  lcd.begin(); 
  lcd.backlight(); 
  //lcd.print("ARA ARA...");
}

void displayInfo(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(user_id);
  lcd.setCursor(0,1);
  
  lcd.print(GPS_LAT,3);
  lcd.print("   ");
  lcd.print(GPS_LNG,3); 
}
/* */


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

String getJson()
{
        DynamicJsonBuffer jsonBuffer;
        JsonObject &root = jsonBuffer.createObject();
        JsonArray &gps_coord = root.createNestedArray("GPS");
        /*
        float lat;
        float lng;
        */
        updateGPS();
        displayInfo();
        
        gps_coord.add(GPS_LAT);
        gps_coord.add(GPS_LNG);
        //root["GPS"] = getGPS();
        root["RSSI"] = getRSSI();
        root["Temperature"] = getTemperature();
        root["Humidity"] = getHumidity();
        root["Gas"] = getGas();
        root["AQI"] = getAQI();
        root["MAC"] = WiFi.macAddress();
        root["C_Protocol"] = getProtocol();
        root["Time"] = getTime();
        root["IP"] =  WiFi.localIP().toString();
        root["PDR"] = getPDR();
        String json_str;
        root.prettyPrintTo(json_str);
        Serial.println(json_str);

        return json_str;
}

/* MQTT functions */
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
    protocol = root["protocol"].as<String>();
    user_id = root["user_id"].as<String>();    
  }
}

boolean MqttPublishData(const char* topic, String value) {
  boolean conn = clientMQTT.connected();
  
  if (!conn) 
    MqttConnect();
  const char* payload=value.c_str();

  boolean result = clientMQTT.publish(topic,payload);
  
  if(result == true)
    mqtt_sent_packets = mqtt_sent_packets + 1;
  
  return result;
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
/* */

/* CoAP functions*/
void callback_response(CoapPacket &packet, IPAddress ip, int port){
  Serial.println("[COAP] Response got");
      
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = NULL;
  coap_sent_packets = coap_sent_packets + 1;
  Serial.println(p);
}

void CoapConfiguration(){
  Coap_Config = true;
  coap.response(callback_response);
  coap.start();  
}
/* */

/* HTTP GET functions */
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
      protocol = root["protocol"].as<String>();
      user_id = root["user_id"].as<String>();
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

/* HTTP POST functions*/
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

        if(httpResponseCode >= 200 && httpResponseCode <= 299) 
          http_sent_packets = http_sent_packets +1;

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
  DisplayConfiguration ();
  WifiConnection();

  neogps.begin(9600, SERIAL_8N1, RXD2, TXD2);
  
  if(protocol == (String)"MQTT")
    MqttConfiguration();
  else if(protocol == (String)"COAP")
    CoapConfiguration();

  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

void loop() {
  if ((millis() - last_sample) > sample_frequency) {
    lcd.clear();
    Serial.println();
    Serial.println("======================");
    Serial.print("Timer set to ");
    Serial.println(sample_frequency);

      if (protocol==(String)"HTTP")
      {
        Serial.println();
        Serial.println("Using HTTP");
        String page = "";
        page = setParametersFromServer(serverNameGet);
        
        
        HTTPost(serverNamePost,getJson());
        http_total_packets = http_total_packets +1;
      }
      else if (protocol==(String)"COAP")
      {
        String page = "";
        page = setParametersFromServer(serverNameGet);
        
        Serial.println();
        Serial.println("Using CoAP");
        
        if(!Coap_Config)
          CoapConfiguration();
          
        coap.put(COAP_SERVER, COAP_PORT, update_api, getJson().c_str());
        coap_total_packets = coap_total_packets +1;
      }      
      else if (protocol==(String)"MQTT")
      {
        Serial.println();
        Serial.println("Using Mqtt");
        if(!MqttConfig)
          MqttConfiguration();

        
        boolean published_data = MqttPublishData(data_topic,getJson());
        mqtt_total_packets = mqtt_total_packets +1;
        Serial.print("[MQTT] Data published: ");
        Serial.println(published_data);
      }
      
      last_sample = millis();
  }
  if(protocol == (String)"COAP"){
    if(!coap.loop()){
      Serial.println("[COAP] Disconnected to server");
      Coap_Config = false;
     }
  }
  else if(protocol == (String)"MQTT"){
    //clientMQTT.loop();
    if (!clientMQTT.loop()){
      //clientMQTT.disconnect();
      Serial.println("[MQTT]Disconnected to Broker");
      MqttConfig = false;
    }
   }
}
