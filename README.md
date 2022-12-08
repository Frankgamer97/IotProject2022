# IotProject2022

To run the Arduino sketch esp32 in the relative directory you need to install the following libraries:<br>
<ul>
  <li>HTTPClient</li>
  <li>PubSubClient</li>
  <li>Coap-simple</li>
  <li>TinyGPS++</li>
  <li>LiquidCrystal_I2C</li>
  <li>DHT</li>
  <li>ArduinoJson</li>
  <li>MeanFilterLib</li>
</ul>

First you need to install all the required libraries with the following command:<br>
```console
pip install -r requirements.txt
```
To run the proxy server you need to execute the following command: <br>
```shell
cd Project
python app.py -ip <IP ADDRESS> -measurements <InfluxDB measurement>
```

To run the Meteostat code you need to run the following command: <br>
```console
cd Project
python Meteo.py
```
