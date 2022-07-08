/*
  Complete project details at Complete project details at https://RandomNerdTutorials.com/esp32-http-get-post-arduino/
*/
#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> //v5.13.5
#include "MeanFilterLib.h" //https://github.com/luisllamasbinaburo/Arduino-Meanfilter
//#include <WifiLocation.h> //https://github.com/gmag11/WifiLocation

#define AQInum 5
#define DHTPIN 15
#define DHTTYPE DHT22

#define MQ2PIN 34

const char ssid[] = "TIM-03859326";
const char password[] = "f5R235Dhc5bdYbCUtGfKH6zP";

//const char* googleApiKey = "AIzaSyDfWfv8Ueu32tOjWw70PjDb1g3S3AGyo2w";
//WifiLocation location(googleApiKey);

//Your Domain name with URL path or IP address with path
const char* serverName = "http://192.168.1.4:5000/update-sensor";

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
float RSS = 0;

MeanFilter<float> meanFilter(AQInum);
DHT dht(DHTPIN,DHTTYPE);


void setMinThreshold(float thresh)
{
  min_gas_value = thresh;
}

void setMaxThreshold(float thresh)
{
  max_gas_value = thresh;
}

void setDelay(unsigned long timer)
{
  sample_frequency = timer;
}


float getGPS(int l)
{
  if (l==0)
  {
    gps=44.083626;
    return gps;
  }
  else{
    gps=12.534610;
    return gps;
  }
}

float getRSSI()
{
  RSS = WiFi.RSSI();
}

float getTemperature()
{
  temperature = 0;//dht.readTemperature();
}

float getHumidity()
{
  humidity = 0;//dht.readHumidity();
}

float getGas()
{
  gas = 10;//analogRead(MQ2PIN);
  meanFilter.AddValue(gas);
  return gas;
}


int getAQI()
{
  float avg = meanFilter.GetFiltered();
  if (avg>=max_gas_value){
    return 0;    
  }
  else if (avg >=min_gas_value and avg< max_gas_value)
  {
    return 1;
  }
  else
  {
    return 2;
  }
}

void WifiConnection(){

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());

}

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(MQ2PIN,INPUT);
  WifiConnection();
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

  
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
          
        // Free resources
        http.end();
      
        
    }
    else {
      Serial.println("WiFi Disconnected");
    }
    

  
}


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
        String json_str;
        root.prettyPrintTo(Serial);
        Serial.println();
        root.prettyPrintTo(json_str);
        return json_str;
}

void loop() {
  if ((millis() - last_sample) > sample_frequency) {
      Serial.println("======================");
      Serial.print("Timer set to ");
      Serial.println(sample_frequency);
/*
        StaticJsonBuffer<200> jsonBuffer;
        JsonObject &root = jsonBuffer.createObject();
        root["GPS"] = getGPS();
        root["RSSI"] = getRSSI();
        root["Temperature"] = getTemperature();
        root["Humidity"] = getHumidity();
        root["Gas"] = getGas();
        root["MAC"] = WiFi.macAddress();
        root.printTo(Serial);
        Serial.println();
        char json_str[100];
        root.prettyPrintTo(json_str, sizeof(json_str));
*/

/*

        DynamicJsonBuffer jsonBuffer;
        JsonObject &root = jsonBuffer.createObject();
        root["GPS"] = getGPS();
        root["RSSI"] = getRSSI();
        root["Temperature"] = getTemperature();
        root["Humidity"] = getHumidity();
        root["Gas"] = getGas();
        root["MAC"] = WiFi.macAddress();

        root.prettyPrintTo(Serial);
        Serial.println();
        Serial.println(sizeof(jsonBuffer));
        Serial.println(sizeof(root));

        
        String json_str;
        root.prettyPrintTo(json_str);//, sizeof(json_str));
        
*/


/*
    location_t loc = location.getGeoFromWiFi();

    Serial.println("Location request data");
    Serial.println(location.getSurroundingWiFiJson());
    Serial.println("Latitude: " + String(loc.lat, 7));
    Serial.println("Longitude: " + String(loc.lon, 7));
    Serial.println("Accuracy: " + String(loc.accuracy));

*/

  
        HTTPost(serverName,getJson());
        last_sample = millis();
        //Serial.println("======================");
  }

}
