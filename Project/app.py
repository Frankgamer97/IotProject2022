from flask import Flask, make_response, request, redirect, url_for, abort, flash, session, jsonify, render_template
from flask_bootstrap import Bootstrap

from Mqtt import MqttHandler
from CoAP import CoapHandler

from utility import SERVER_MEASUREMENTS, current_protocol, listvalues, post_parameters, influx_parameters, mqtt_handler, coap_handler
from utility import get_time, is_int, get_protocol, get_IP
from influxdb import influxdb_post
from aggregation import Aggregation
from TelegramBotHandler import TelegramBotHandler

import os

aggr = Aggregation()
bot_handler = TelegramBotHandler(aggr)



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
    json_data = request.json
    #mac = json_data["MAC"]
    #GPS= json_data["GPS"]
    #rssi = json_data["RSSI"]
    #Temperature = json_data["Temperature"]
    #Humidity = json_data["Humidity"]
    #Gas = json_data["Gas"]
    #AQI = json_data["AQI"]

    global current_protocol
    current_protocol = json_data["C_Protocol"]
    
    json_data["Time"] = get_time()
    if len(listvalues) >= SERVER_MEASUREMENTS:
        del listvalues[-1]
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
    # influxdb_post(json_data) # IMPORTANTE!!!!
    bot_handler.telegram_updates()
    
    return "ok"



#esp32 take values from the json post_parameters
@app.route("/get-sensor/", methods=('GET', 'POST'))
def getsensor():
    #to write a json inizialize the variable with the name of the attribute
    #ex: sample_frequency=100       ==>   {"sample_frequency":"100"}
    return jsonify(
        post_parameters
        #sample_frequency=post_parameters["sample_frequency"],
        #min_gas_value=post_parameters["min_gas_value"],
        #max_gas_value=post_parameters["max_gas_value"],
        #protocol=post_parameters["protocol"],
    )


#a little form to update the json post_parameters
@app.route('/set-parameters/', methods=('GET', 'POST'))
def setparams():
    if request.method == 'POST':
        
        MAC = request.form['MAC']
        sample_frequency = request.form['sample_frequency']
        min_gas_value = request.form['min_gas_value']
        max_gas_value = request.form['max_gas_value']
        protocol = request.form.get('comp_select')

        is_ok = True

        if not MAC:
            MAC = ""
        if not sample_frequency:
            sample_frequency=post_parameters["sample_frequency"]# flash('frequency is required!'.upper(), "alert")
        if not is_int(sample_frequency):
            is_ok = False
            flash('frequency must be a number!'.upper(), "alert")
        elif not int(sample_frequency) >= 0:
            is_ok = False
            flash('negative sample frequency!'.upper(), "alert")

        if not min_gas_value:
            min_gas_value = post_parameters["min_gas_value"]# flash('min gas value is required!'.upper(), "alert")
        if not is_int(min_gas_value):
            is_ok = False
            flash('min gas value must be a number!'.upper(), "alert")
        if not max_gas_value:
            max_gas_value = post_parameters["max_gas_value"]# flash('max gas value is required!'.upper(), "alert")
        if not is_int(max_gas_value):
            is_ok = False
            flash('max gas value  must be a number!'.upper(), "alert")
        if is_int(min_gas_value) and is_int(max_gas_value) and ( not (int(min_gas_value) < int(max_gas_value))):
            is_ok = False
            flash('gas value range is incorrect!'.upper(), "alert")
        
        if is_ok:
            post_parameters['MAC']= MAC
            post_parameters['sample_frequency']= sample_frequency
            post_parameters['min_gas_value']= min_gas_value
            post_parameters['max_gas_value']= max_gas_value
            post_parameters['protocol']= get_protocol(protocol)

            
            if current_protocol == "HTTP":
                pass
            if current_protocol == "MQTT":
                mqtt_handler.update_config(post_parameters)
            
            if current_protocol == "COAP":
                pass
                
            flash('Parameters updated'.upper(), "success")
            # return redirect(url_for('index'))

    protocols=[{'name':'HTTP'}, {'name':'COAP'}, {'name':'MQTT'}]
    return render_template('set_parameters.html',prot=protocols)


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

    ip=get_IP()

    mqtt_handler = MqttHandler(listvalues, bot_handler)
    coap_handler = CoapHandler(listvalues, bot_handler)
   # bot_handler = TelegramBotHandler(aggr)
    

    app.run(host=ip,port=5000)


    mqtt_handler.mqtt_thread.join(0)
    coap_handler.coap_thread.join(0)
  #  bot_handler.telegram_thread.join(0)
    #bot_handler.join(0)

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

