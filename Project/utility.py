from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import pytz
import os

SERVER_MEASUREMENTS = 7

def get_time():

    #utc_dt = datetime.now(timezone.utc) # UTC time
    #dt = utc_dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    tz = pytz.timezone('Europe/Rome')
    return datetime.now(tz)
    
    
def is_int(data):
    try:
        isinstance(int(data), int)
        return 1
    except:
        return 0
    
def get_protocol(prot):
    if prot=="HTTP":
        return 0
    elif prot=="COAP":
        return 1
    elif prot=="MQTT":
        return 2

def influxdb_post(json_data):
    
    token = "7pTF08iW5yei6u8-8679-FnOPrLyjuBZm6l9mRbwTZZgwdqyMhjLRYUGm9axjZzVqppnSNU0gCkJ9JlPTUVgag=="
    org = "primiarmi.pac@gmail.com"
    bucket = "esp32"

    client = InfluxDBClient(url="https://europe-west1-1.gcp.cloud2.influxdata.com", token=token, org=org)

    write_api = client.write_api(write_options=SYNCHRONOUS)


    mac = json_data["MAC"]
    GPS= json_data["GPS"]
    rssi = json_data["RSSI"]
    Temperature = json_data["Temperature"]
    Humidity = json_data["Humidity"]
    Gas = json_data["Gas"]
    AQI = json_data["AQI"]
    Time = json_data["Time"]
    

    print(json_data)
    
    point = Point("mamma") \
        .tag("Device", mac) \
        .tag("GPS", GPS) \
        .field("RSSI", rssi) \
        .field("Temperature", Temperature) \
        .field("Humidity", Humidity) \
        .field("Gas", Gas) \
        .field("AQI", AQI) \
        .time(Time, WritePrecision.NS)


    #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
    write_api.write(bucket, org, point)
 
    return "ok"

