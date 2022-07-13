from flask import Flask, make_response, request, redirect, url_for, abort, flash, session, jsonify, render_template
from flask_bootstrap import Bootstrap

from Mqtt import MqttHandler

from utilities import get_data, is_int, get_protocol, influxdb_post
import os


current_protocol = "HTTP"
listvalues = []
post_parameters = {'sample_frequency': "5000",
             'min_gas_value': "0",
             'max_gas_value': "10000",
             'protocol': "0"}



mqtt_handler = MqttHandler(listvalues)

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
    
    json_data["Time"] = get_data()
    if len(listvalues)>7:
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

    
    return "ok"

#esp32 take values from the json post_parameters
@app.route("/get-sensor/", methods=('GET', 'POST'))
def getsensor():
    #to write a json inizialize the variable with the name of the attribute
    #ex: sample_frequency=100       ==>   {"sample_frequency":"100"}
    return jsonify(
        sample_frequency=post_parameters["sample_frequency"],
        min_gas_value=post_parameters["min_gas_value"],
        max_gas_value=post_parameters["max_gas_value"],
        protocol=post_parameters["protocol"],
    )

#a little form to update the json post_parameters
@app.route('/set-parameters/', methods=('GET', 'POST'))
def setparams():
    if request.method == 'POST':
        

        sample_frequency= request.form['sample_frequency']
        min_gas_value = request.form['min_gas_value']
        max_gas_value = request.form['max_gas_value']
        protocol = request.form.get('comp_select')

        is_ok = True

        if not sample_frequency:
            sample_frequency=post_parameters["sample_frequency"]# flash('frequency is required!'.upper(), "alert")
        if not is_int(sample_frequency):
            is_ok = False
            flash('frequency must be a number!'.upper(), "alert")
        if not int(sample_frequency) >= 0:
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
        if not (int(min_gas_value) < int(max_gas_value)):
            is_ok = False
            flash('gas value range is incorrect!'.upper(), "alert")
        
        if is_ok:
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


    protocols=[{'name':'HTTP'}, {'name':'COAP'}, {'name':'MQTT'}]
    return render_template('set_parameters.html',prot=protocols)


#flask run --host=0.0.0.0

if __name__ == '__main__':

    app.run(host='0.0.0.0',port=5000)
    mqtt_handler.mqtt_thread.join(0)
    #  from livereload import Server
    #  server = Server(app.wsgi_app)
    #  server.serve(host = '0.0.0.0',port=5000)
    #,extra_files=listvalues)
    # server = Thread(target=_run)
    # server.start()
    # mqtt_handler.subscribe_updates()
    # server.join()

