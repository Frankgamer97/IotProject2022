# from lib2to3.pytree import _Results
from pdb import post_mortem
from struct import pack
from flask import Flask, make_response, request, redirect, url_for, abort, flash, session, jsonify, render_template
from flask_bootstrap import Bootstrap

from Mqtt import MqttHandler
from CoAP import CoapHandler

from utility import SERVER_MEASUREMENTS, current_protocol, listvalues, influx_parameters, mqtt_handler, coap_handler
from utility import get_time, is_int, get_protocol, get_IP, get_device_time, influxdb_measurement
from utility import get_ntp_time, getDeviceId, getAllDevices, getMac, getConfig,getFirstConfig
from utility import sort_protocol, getConfigByUserId, setMac, getIpByUserId, updateConfigProtocol
from utility import post_parameters,jsonpost2pandas

from utility import graph_meta, graph_intervall
from influxdb import influxdb_post
from aggregation import Aggregation
from TelegramBotHandler import TelegramBotHandler
from DataStorage import StorageHandler

from datetime import datetime

import pybase64
import copy
from io import BytesIO
from matplotlib.figure import Figure
# from DeviceStatHandler import DeviceStatHandler

import os
import pandas as pd

aggr = Aggregation()
bot_handler = TelegramBotHandler(aggr)
http_startMeasurements = None


#app = Flask(__name__, template_folder='templates')
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
Bootstrap(app)



# 404 #INUTILE
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
    return render_template('tables.html', messages=listvalues)


# esp32 post its value to the list listvalues
@app.route('/update-sensor/', methods=['GET', 'POST'])
def updatesensor():
    
    #mac = json_data["MAC"]
    #GPS= json_data["GPS"]
    #rssi = json_data["RSSI"]
    #Temperature = json_data["Temperature"]
    #Humidity = json_data["Humidity"]
    #Gas = json_data["Gas"]
    #AQI = json_data["AQI"]

    global aggr
    # global current_protocol

    json_data = request.json           
    
    # print("[POST] CURRENT PROTOCOL ========> ", current_protocol["current_protocol"])
    sent_time = None
    recv_time = None 
    packet_delay = 0

    try:
        sent_time = get_device_time(json_data["Time"])# datetime(year, month, day, hour, minute, second)
        recv_time = get_ntp_time()
    except:
        print("[WARNING] NTP SERVER NO RESPONSE")
        
        if recv_time is None:
            recv_time = datetime.now()
        if sent_time is None:
            sent_time = recv_time

    packet_delay = (recv_time - sent_time).total_seconds()

    json_data["Delay"] = packet_delay
    json_data["PDR"] = aggr.get_packet_delivery_ratio(json_data["C_Protocol"])
    json_data["Time"] = get_time()
    
    if len(listvalues) >= SERVER_MEASUREMENTS:
        del listvalues[-1]
    # print("REMOTE ADDRESS:---->",request.remote_addr)
    getConfig(json_data["IP"])
    json_data["DeviceId"] = getDeviceId(json_data["IP"])
    setMac(json_data["IP"], json_data["MAC"])

    current_protocol["current_protocol"]= json_data["C_Protocol"]
    updateConfigProtocol(json_data["IP"], json_data["C_Protocol"])

    listvalues.insert(0, json_data
                      #{'MAC': mac,
                      #  'GPS': GPS,
                      #  'RSSI': rssi,
                      #  'Temperature': Temperature,
                      #  'Humidity': Humidity,
                      #  'Gas': Gas,
                      #  'AQI': AQI,
                      #  'Protocol': current_protocol
                      #  }
                       )
    aggr.update_pandas()
    bot_handler.telegram_updates()

    influxdb_post(jsonpost2pandas(json_data), measurement=influxdb_measurement,tag_col=["Device","GPS"]) # IMPORTANTE!!!!


    return "ok"



#esp32 take values from the json post_parameters
@app.route("/get-sensor/", methods=('GET', 'POST'))
def getsensor():
    #to write a json inizialize the variable with the name of the attribute
    #ex: sample_frequency=100       ==>   {"sample_frequency":"100"}

    config = getConfig(request.remote_addr)

    return jsonify(
        config# post_parameters
        #sample_frequency=post_parameters["sample_frequency"],
        #min_gas_value=post_parameters["min_gas_value"],
        #max_gas_value=post_parameters["max_gas_value"],
        #protocol=post_parameters["protocol"],
    )


#a little form to update the json post_parameters
@app.route('/set-parameters/', methods=('GET', 'POST'))
def setparams():
    is_ok = True

    if request.method == 'POST':
        
        # global current_protocol

        # print("CURRENT PROTOCOL [PRE UPDATING]======> ", current_protocol["current_protocol"])

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

            # is_ok = True

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
                remote_configs['protocol']= protocol# get_protocol(protocol)

                if current_protocol["current_protocol"] == "HTTP":
                    pass
                if current_protocol["current_protocol"] == "MQTT":
                    # print("SONO QUI")
                    mqtt_handler.update_config(remote_configs)
                
                if current_protocol["current_protocol"] == "COAP":
                    pass

                current_protocol["current_protocol"] = protocol
                    
                flash('Parameters updated'.upper(), "success")
                # return redirect(url_for('index'))
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
        # print("[SET-PARAM] remote config", remote_configs)
        protocols = sort_protocol(remote_configs, protocols)
        
        devices = getAllDevices()
        # devices.append("Mucciacia")

        devices_config = getConfigByUserId()
        # devices_config["Mucciacia"] = {
        #         'MAC':"Giovanni",
        #         'user_id':"Mucciacia",
        #         'sample_frequency': "75000",
        #         'min_gas_value': "50",
        #         'max_gas_value': "95000",
        #         'protocol': "2"
        #         }
        #

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
    data = {"graphs": ["Delay","Ratio"], "first_image": image, "intervall": graph_intervall}

    return render_template('graphs.html', data=data)

@app.route("/getGraph/",methods=['GET'])
def getGraph():
    global aggr
    graph =request.args.get('graph')



    image = aggr.build_graph(graph, graph_meta[graph]["label"], graph_meta[graph]["title"])

    return image

@app.route('/aggregation/')
def aggregation():
    return render_template('aggregation.html')




#GET TABLES AT RUNTIME
@app.route('/aggregate')
def aggregate():
    #print(aggr.build_aggregate())
    return render_template('aggregate.html', messages=aggr.build_aggregate())

#flask run --host=0.0.0.0
if __name__ == '__main__':
    StorageHandler.create_tmp_directories()
    ip=get_IP()

    mqtt_handler = MqttHandler(listvalues, bot_handler, aggr)
    coap_handler = CoapHandler(listvalues, bot_handler, aggr, SERVER_IP=ip)
    # stat_handler = DeviceStatHandler.control_updates()
    

    app.run(host=ip,port=5000)

    mqtt_handler.mqtt_thread.join(0)
    coap_handler.coap_thread.join(0)
    # bot_handler.join(0)
    # stat_handler.join(0)
    



    #ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
    #print("------>",ip)

    #  from livereload import Server
    #  server = Server(app.wsgi_app)
    #  server.serve(host = '0.0.0.0',port=5000)
    #,extra_files=listvalues)
    # server = Thread(target=_run)
    # server.start()
    # mqtt_handler.subscribe_updates()
    # server.join()

