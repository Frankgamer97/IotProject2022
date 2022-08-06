from copy import deepcopy
from datetime import datetime
from argparse import ArgumentParser

import ntplib
import pytz
import pandas as pd

proxy_data_window = 17
proxyData = []

ip_dict = {"value": "192.168.4.1"}
current_protocol = {"current_protocol": "HTTP"}

mqtt_handler = None
coap_handler = None

ArimaForecastSample = 5
ArimaPastSample = 5

ArimaCountUpdates = 0
ArimaMaxUpdate = ArimaForecastSample
ArimaDFPost = pd.DataFrame()

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
             'measurement': "test-august6-1"
             }

telegram_bot_update_frequency = 20

graph_meta={
    "Delay": {"label": "Seconds", "title": "Average Delay"},
    "Ratio": {"label": "PDR", "title": "Average PDR"},

    "Arima Temperature": {"title": "Forecast Temperature"},
    "Arima Humidity": {"title": "Forecast Humidity"},
    "Arima Gas": {"title": "Forecast Gas"}
}

graph_intervall = 2500

ip_userid_dict = {}
userid_ip_dict = {}

# userid_gps = {"Pippo Baudo": [40.661,17.695], "Giovanni Mucciacia": [40.662,17.696]}
userid_gps = {}

ip_mac_dict = {}
ip_config_dict = {}


def set_tunable_window(n):
    global proxy_data_window
    proxy_data_window = n

def updateProxyData(json_data):
    global proxyData, proxy_data_window

    proxyData_len = len(proxyData)
    if proxyData_len >= proxy_data_window:
        for _ in range(proxyData_len - proxy_data_window):
            del proxyData[-1]

    proxyData.insert(0, json_data)
    
def get_time():
    tz = pytz.timezone('UTC')
    return datetime.now(tz)

def get_ntp_time():
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('uk.pool.ntp.org', version=3)
    return datetime.utcfromtimestamp(response.tx_time)
    
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
    return ip_dict["value"]

def set_IP(new_ip):
    ip_dict["value"] = new_ip

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
    
    json_post = json_post[["Time","Device","GPS","RSSI","Gas","AQI","Temperature","Humidity"]]

    return json_post

def sort_protocol(config, protocol_list):
    ordered = []

    config_protocol = str(config["protocol"])
    ordered.append(config_protocol)
    
    for protocol in protocol_list:
        if protocol != ordered[0]:
            ordered.append(protocol)

    return ordered

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

def updateGps(userid, coordinates):
    userid_gps[userid] = coordinates

def buildParser():
    parser=ArgumentParser()
    parser.add_argument("-ip",dest="remote_ip", type=str, default=get_IP())
    parser.add_argument("-measurement",dest="measurement", type=str, default=influx_parameters["measurement"])
    parser.add_argument("-data_window",dest="data_window", type=str, default=proxy_data_window)

    return parser

def acquireInputParameters():
    parser = buildParser()
    args = parser.parse_args()
    set_IP(args.remote_ip)
    influx_parameters["measurement"] = args.measurement
    set_tunable_window(args.data_window)
