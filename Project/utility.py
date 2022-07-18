from datetime import datetime, timezone

import pytz
import os
import socket  

SERVER_MEASUREMENTS = 19

current_protocol = "HTTP"

mqtt_handler = None
coap_handler = None

listvalues = []


ip = "192.168.1.254"


post_parameters = {
             'MAC':"",
             'sample_frequency': "5000",
             'min_gas_value': "0",
             'max_gas_value': "10000",
             'protocol': "0"
             }

influx_parameters = {
             'user':"primiarmi.pac@gmail.com",
             'token': "7pTF08iW5yei6u8-8679-FnOPrLyjuBZm6l9mRbwTZZgwdqyMhjLRYUGm9axjZzVqppnSNU0gCkJ9JlPTUVgag==",
             'bucket': "esp32",
             'server': "https://europe-west1-1.gcp.cloud2.influxdata.com",
             'measurement': "mamma"
             }


telegram_api_key = "5509057193:AAHxI7t17bDev0WfgA_V_jC9I_ZcgjGxRvw" 
telegram_chat_id = "-1001781808448"

def set_tunable_window(n):
    SERVER_MEASUREMENTS = n

def get_time():

    #utc_dt = datetime.now(timezone.utc) # UTC time
    #dt = utc_dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    tz = pytz.timezone('Europe/Rome')
    return datetime.now(tz)
    
def get_IP():
    #hostname=socket.gethostname()   
    #IPAddr=socket.gethostbyname(hostname)   
    #print("Your Computer Name is:"+hostname)   
    #print("Your Computer IP Address is:"+IPAddr)
    #return IPAddr
    return ip

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

