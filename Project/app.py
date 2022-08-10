from gc import callbacks
from time import sleep
from flask_bootstrap import Bootstrap
from flask import Flask, request, abort, flash, jsonify, render_template
from os import getenv

from datetime import datetime

from utility import current_protocol, proxyData, influx_parameters, mqtt_handler
from utility import coap_handler, graph_meta, graph_intervall, userid_gps
from utility import get_time, is_int, get_IP, get_device_time 
from utility import get_ntp_time, getDeviceId, getAllDevices, getMac, getConfig,getFirstConfig
from utility import sort_protocol, getConfigByUserId, setMac, getIpByUserId, updateConfigProtocol
from utility import updateGps, updateProxyData, acquireInputParameters

from influxdb import send_influxdb
from Aggregation import Aggregation

from TelegramBotHandler import TelegramBotHandler
from DataStorage import StorageHandler
from ArimaModel import ForecastHandler
from Mqtt import MqttHandler
from CoAP import CoapHandler

acquireInputParameters()

aggr = Aggregation()
bot_handler = TelegramBotHandler(aggr)
arima_handler=ForecastHandler(influx_parameters["measurement"])


#app = Flask(__name__, template_folder='templates')
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = getenv('SECRET_KEY', 'secret string')
Bootstrap(app)

# 404 
@app.route('/404')
def not_found():
    abort(404)

#Main page with results
@app.route('/')
def index():
    return render_template('index.html')

#GET TABLES AT RUNTIME
@app.route('/tables')
def tables():
    return render_template('tables.html', messages=proxyData)

 
# esp32 post its value to the list proxydata
@app.route('/update-sensor/', methods=['GET', 'POST'])
def updatesensor():
    global aggr
    json_data = request.json           
    sent_time = None
    recv_time = None 
    packet_delay = 0

    try:
        sent_time = get_device_time(json_data["Time"])# datetime(year, month, day, hour, minute, second)
        recv_time = get_ntp_time()
        packet_delay = (recv_time - sent_time).total_seconds()
    except:
        print("[WARNING] NTP SERVER NO RESPONSE")
    

    json_data["Delay"] = packet_delay
    # json_data["PDR"] = aggr.get_packet_delivery_ratio(json_data["C_Protocol"])
    json_data["Time"] = get_time()
    
    getConfig(json_data["IP"])
    json_data["DeviceId"] = getDeviceId(json_data["IP"])
    setMac(json_data["IP"], json_data["MAC"])

    json_data["GPS"] = [ round(x,3) for x in json_data["GPS"]]
    updateGps(json_data["DeviceId"], json_data["GPS"])

    current_protocol["current_protocol"]= json_data["C_Protocol"]
    updateConfigProtocol(json_data["IP"], json_data["C_Protocol"])

    updateProxyData(json_data)
    aggr.update_pandas()

    send_influxdb(json_data, measurement = influx_parameters["measurement"])

    arima_handler.arima_updates()
    bot_handler.telegram_updates()

    # momo = datetime.now()
    # print("I am waiting")
    # while True:
    #     momo2 = datetime.now()
    #     if (momo2 - momo).total_seconds() >=3:
    #         break
    return "ok"

#esp32 take values from the json post_parameters
@app.route("/get-sensor/", methods=('GET', 'POST'))
def getsensor():
    #to write a json inizialize the variable with the name of the attribute
    #ex: sample_frequency=100       ==>   {"sample_frequency":"100"}

    config = getConfig(request.remote_addr)
    return jsonify(config)

#a little form to update the json post_parameters
@app.route('/set-parameters/', methods=('GET', 'POST'))
def setparams():
    is_ok = True

    if request.method == 'POST':
        if len(getAllDevices()) == 0 or not request.form.get('DeviceId'):
            is_ok = False
            flash('No device found'.upper(), "alert")
        
        else:
            userid = request.form.get('DeviceId')
            remote_ip = getIpByUserId(userid)
            MAC = getMac(remote_ip) 
            remote_configs = getConfig(remote_ip)
            
            sample_frequency = request.form['sample_frequency']
            min_gas_value = request.form['min_gas_value']
            max_gas_value = request.form['max_gas_value']
            protocol = request.form.get('comp_select')

            if not MAC:
                MAC = ""
            if not sample_frequency:
                sample_frequency=remote_configs["sample_frequency"]# flash('frequency is required!'.upper(), "alert")
            if not is_int(sample_frequency):
                is_ok = False
                flash('frequency must be a number!'.upper(), "alert")
            elif not int(sample_frequency) >= 0:
                is_ok = False
                flash('negative sample frequency!'.upper(), "alert")

            if not min_gas_value:
                min_gas_value = remote_configs["min_gas_value"]# flash('min gas value is required!'.upper(), "alert")
            if not is_int(min_gas_value):
                is_ok = False
                flash('min gas value must be a number!'.upper(), "alert")
            if not max_gas_value:
                max_gas_value = remote_configs["max_gas_value"]# flash('max gas value is required!'.upper(), "alert")
            if not is_int(max_gas_value):
                is_ok = False
                flash('max gas value  must be a number!'.upper(), "alert")
            if is_int(min_gas_value) and is_int(max_gas_value) and ( not (int(min_gas_value) < int(max_gas_value))):
                is_ok = False
                flash('gas value range is incorrect!'.upper(), "alert")
            
            if is_ok:
                remote_configs['MAC']= MAC
                remote_configs['user_id']= userid
                remote_configs['sample_frequency']= sample_frequency
                remote_configs['min_gas_value']= min_gas_value
                remote_configs['max_gas_value']= max_gas_value
                remote_configs['protocol']= protocol

                if current_protocol["current_protocol"] == "HTTP":
                    pass
                if current_protocol["current_protocol"] == "MQTT":
                    mqtt_handler.update_config(remote_configs)
                
                if current_protocol["current_protocol"] == "COAP":
                    pass

                current_protocol["current_protocol"] = protocol
                    
                flash('Parameters updated'.upper(), "success")
    else:
        remote_configs = getFirstConfig()

    #print("REMOTe PROTOCOL:------>", remote_configs)
    # protocols=[{'name':'HTTP'}, {'name':'COAP'}, {'name':'MQTT'}]

    protocols = ['HTTP', 'COAP', 'MQTT']
    data = {
            "protocols": protocols,
            "devices": [],
            "config": {},
            "total_configs": {}
        }

    if is_ok:
        protocols = sort_protocol(remote_configs, protocols)
        
        devices = getAllDevices()
    
        devices_config = getConfigByUserId()

        data = {
            "protocols": protocols,
            "devices": devices,
            "config": remote_configs,
            "total_configs": devices_config
        }

    return render_template('set_parameters.html', data=data)


# check influx params
@app.route("/get-influxdb/", methods=('GET', 'POST'))
def getinfluxdb():
    #to write a json inizialize the variable with the name of the attribute
    #ex: sample_frequency=100       ==>   {"sample_frequency":"100"}
    return jsonify(influx_parameters)

#a form to update the influx parameters
@app.route('/set-influxdb/', methods=('GET', 'POST'))
def setinfluxdb():
    if request.method == 'POST':
        
        user = request.form['user']
        token = request.form['token']
        bucket = request.form['bucket']
        server = request.form['server']
        measurement = request.form['measurement']

        is_ok = True

        if not user:
            user=influx_parameters["user"]
        if not token:
            token=influx_parameters["token"]
        if not bucket:
            bucket=influx_parameters["bucket"]
        if not server:
            server=influx_parameters["server"]
        if not measurement:
            measurement=influx_parameters["measurement"]

        if is_ok:
            influx_parameters['user']= user
            influx_parameters['token']= token
            influx_parameters['bucket']= bucket
            influx_parameters['server']= server
            influx_parameters['measurement']= measurement
                  
            flash('Parameters updated'.upper(), "success")
            # return redirect(url_for('index'))

    return render_template('set_influxdb.html')

@app.route('/graphs/', methods=['GET'])
def graphs():
    global graph_intervall
    global graph_meta
    global aggr

    image = aggr.build_graph("Delay", graph_meta["Delay"]["label"], graph_meta["Delay"]["title"])
    data = {"graphs": list(graph_meta.keys()), "first_image": image, "intervall": graph_intervall}

    return render_template('graphs.html', data=data)

@app.route("/getGraph/",methods=['GET'])
def getGraph():
    global aggr
    graph =request.args.get('graph')
    
    if graph == "Delay" or graph == "PDR" or graph == "PPR":
        image = aggr.build_graph(graph, graph_meta[graph]["label"], graph_meta[graph]["title"])

    elif "Arima" in graph:
        image_name = graph.split(" ")[1]
        image = arima_handler.images[image_name]

    else:
        print("[getGraph] WARNING: unknown image selected")

    return image

@app.route("/map/", methods=['GET'])
def map():
    global userid_gps
    data = {}
    
    data["coordinates"] = userid_gps
    
    userid_keys = list(userid_gps.keys())
    data["users"] = str(userid_keys)

    if len(userid_keys) == 0:
        data["first_coordinates"] = "[41.890309,12,492510]" 
    else:
        data["first_coordinates"] = userid_gps[userid_keys[0]]

    return render_template('maps.html', data = data)

@app.route("/getCoord/", methods=['GET'])
def getCoord():
    
    global userid_gps
    
    users = list(userid_gps.keys())
    for userid in users:
        userid_gps[userid] = [userid_gps[userid][0], userid_gps[userid][1]]
    return userid_gps

@app.route('/aggregation/')
def aggregation():
    return render_template('aggregation.html')

#GET TABLES AT RUNTIME
@app.route('/aggregate')
def aggregate():
    return render_template('aggregate.html', messages=aggr.build_aggregate())

#flask run --host=0.0.0.0
if __name__ == '__main__':

    StorageHandler.create_tmp_directories()

    mqtt_handler = MqttHandler(bot_handler, arima_handler, aggr)
    coap_handler = CoapHandler(bot_handler, arima_handler, aggr)

    ip=get_IP()
    app.run(host=ip,port=5000)

    mqtt_handler.mqtt_thread.join(0)
    coap_handler.coap_thread.join(0)