from datetime import datetime, timezone
from copy import deepcopy
from operator import pos
import ntplib

import pytz
import os
import socket  
import pandas as pd

import threading
# import Queue












SERVER_MEASUREMENTS = 17

current_protocol = {"current_protocol": "HTTP"}

mqtt_handler = None
coap_handler = None

influxdb_measurement="test-august-1"
influxdb_forecast_sample = 5
influxdb_past_sample = 5

influxdb_countupdates = 0
influxdb_maxupdate = influxdb_forecast_sample
influxdb_df_post = pd.DataFrame()

listvalues = []

ip = "192.168.1.203"
#{"MAC":"","max_gas_value":"10000","min_gas_value":"0","protocol":"0","sample_frequency":"5000","user_id":""}
post_parameters = {
             'MAC':"",
             'user_id':"",
             'sample_frequency': "5000",
             'min_gas_value': "0",
             'max_gas_value': "10000",
             'protocol': "HTTP"
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
telegram_bot_update_frequency = 5

# stat_data_frequency = 5
# stat_data_delay = 10
stat_data_timeout = 10
stat_data_intervall = 20
graph_meta={
    "Delay": {"label": "Seconds", "title": "Average Delay"},
    "Ratio": {"label": "PDR", "title": "Average PDR"}
}

graph_intervall = 500

ip_userid_dict = {}
userid_ip_dict = {}

ip_mac_dict = {}
ip_config_dict = {}

# user_mac_dict = {} # "user_id: MAC"
# user_ip_dict = {} # 'user_id': 'ip'

# mac_user_dict = {} # "MAC: user_id"

# mac_ip_dict = {} # "MAC: IP"
# ip_configs_dict = {} # "IP: { CONFIGURATION }"


# #######devices_config = {}


def set_tunable_window(n):
    SERVER_MEASUREMENTS = n

def get_time():

    #utc_dt = datetime.now(timezone.utc) # UTC time
    #dt = utc_dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    tz = pytz.timezone('Europe/Rome')
    return datetime.now(tz)

def get_ntp_time():
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('uk.pool.ntp.org', version=3)
    return datetime.fromtimestamp(response.tx_time)
    
def get_device_time(dev_time):
    # "2022 7 22 00 06 16"
    time_array = dev_time.split(" ")
    year = int(time_array[0])
    month = int(time_array[1])
    day = int(time_array[2])
    hour = int(time_array[3])
    minute = int(time_array[4])
    second = int(time_array[5])

    return datetime(year, month, day, hour, minute, second)
    
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

def jsonpost2pandas(json_data):
    drop_columns=["C_Protocol","IP","Delay","PDR","DeviceId"]
    json_post=deepcopy(json_data)

    for key in json_post.keys():
        json_post[key]=[json_post[key]]

    json_post=pd.DataFrame(json_post)
    json_post=json_post.drop(columns=drop_columns, axis=1, errors='ignore').rename(columns = {'MAC':'Device'})
    return json_post

'''
def getMac(user_id):
    return user_mac_dict[user_id]

def getAllDevices():
    return list(user_mac_dict.keys())

def getDeviceId(mac, ip = None):
    mac_keys = mac_user_dict.keys()
    if mac in mac_keys:
        return mac_user_dict[mac]
    else:
        user_id = "Esp32_"+str(len(mac_keys))
        mac_user_dict[mac] = user_id
        user_mac_dict[user_id] = mac

        if ip is None:
            print("[getDeviceId] ERRORE BHOOO")
        else:
            mac_ip_dict[mac] = ip
            user_ip_dict[user_id] = ip
        return user_id

def getRemoteIp(mac):
    if mac in mac_ip_dict.keys():
        return mac_ip_dict[mac]
    return None
'''

'''
def getConfig(ip):
    if ip not in ip_configs_dict.keys():
        ip_configs_dict[ip] = deepcopy(post_parameters)

    return ip_configs_dict[ip]

def getConfigByUserId():
    user_config_dict = {}

    for user, ip in user_ip_dict.items():
        config = ip_configs_dict[ip]
        user_config_dict[user] = config

    return user_config_dict
'''
def sort_protocol(config, protocol_list):
    ordered = []

    # print()
    # print("config protocl: ", config["protocol"])
    # print(type(config["protocol"]))
    # print()

    config_protocol = str(config["protocol"])
    ordered.append(config_protocol)
    
    # if config_protocol == "0":
    #     ordered.append("HTTP")
    # elif config_protocol == "1":
    #     ordered.append("COAP")
    # elif config_protocol == "2":
    #     ordered.append("MQTT")
    # else:
    #     print("[sort_protocols] No config protocol found")

    for protocol in protocol_list:
        if protocol != ordered[0]:
            ordered.append(protocol)

    return ordered




# ip_userid_dict = {}
# userid_ip_dict = {}

# ip_mac_dict = {}
# ip_config_dict = {}


def getDeviceId(ip):
    ip_keys = ip_userid_dict.keys()
    if ip not in ip_keys:
        userid = "Esp32_"+str(len(ip_keys))
        ip_userid_dict[ip] = userid
        userid_ip_dict[userid] = ip

    return ip_userid_dict[ip]

def getIpByUserId(userid):
    return userid_ip_dict[userid] 

def setMac(ip,mac):
    ip_mac_keys = list(ip_mac_dict.keys())
    if ip not in ip_mac_keys:
        ip_mac_dict[ip] = mac

        config = getConfig(ip)
        config["MAC"] = mac

def getMac(ip):
    return ip_mac_dict[ip]
    
def getConfig(ip):
    ip_config_keys = list(ip_config_dict.keys())
    if ip not in ip_config_keys:
        ip_config_dict[ip] = deepcopy(post_parameters)

        userid = getDeviceId(ip)
        # mac = getMac(ip)

        # ip_config_dict[ip]["MAC"] = mac
        ip_config_dict[ip]["user_id"] = userid

    return ip_config_dict[ip]  
        

def getFirstConfig():

    ip_config_keys = list(ip_config_dict.keys())
    if len(ip_config_keys) == 0:
        print("[getFirstConfig] No device found")
        return post_parameters
    return ip_config_dict[ip_config_keys[0]]

def getAllDevices():
    return list(userid_ip_dict.keys())

def getConfigByUserId():
    user_config_dict = {}

    for userid, ip in userid_ip_dict.items():
        config = ip_config_dict[ip]
        user_config_dict[userid] = config

    return user_config_dict

def updateConfigProtocol(ip, protocol):

    assert protocol == "HTTP" or protocol == "COAP" or protocol == "MQTT"
    assert ip in ip_config_dict.keys()
    ip_config_dict[ip]["protocol"] = protocol


def mecojoni(json_data, measurement=influxdb_measurement):

    global countupdates
    global maxupdate
    global df_post
    
    json_post = jsonpost2pandas(json_data)
    if countupdates >= maxupdate:
        countupdates = 0

        try:
            influxdb_post(df_post, measurement=measurement,tag_col=["Device","GPS"]) # IMPORTANTE!!!!
            df_post = pd.DataFrame()
            print("mhhhhfine")
        except:
            print("Too few values to predict")
            pass
    else:
        countupdates += 1
        df_post = df_post.append(json_post)
    