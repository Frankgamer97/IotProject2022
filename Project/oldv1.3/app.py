
# -*- coding: utf-8 -*-

import os,requests
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from markupsafe import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, flash, session, jsonify, render_template
from flask_bootstrap import Bootstrap
from bs4 import BeautifulSoup


from datetime import datetime
import os

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


post_parameters = {'sample_frequency': "5000",
             'min_gas_value': "0",
             'max_gas_value': "10000",
             'protocol': "0"}


listvalues = []#[{'Device': "100",
             #'GPS': [100,11],
             #'Timestamp': "100",
             #'RSSI': "100",
            #'Temperature': "100",
            #'Humidity': "100",
            #'Gas': "100",
            #'AQI': "100"},
            #   
            #{'Device': "100",
            # 'GPS': [100,2],
            # 'Timestamp': "100",
            # 'RSSI': "100",
            #'Temperature': "100",
            #'Humidity': "100",
            #'Gas': "100",
            #'AQI': "100"}]

#TODO: delete
listvalues1 = [{ 'Device': "100",
                 'GPS': [100,11],
                 'Timestamp': "100",
                 'RSSI': "100",
                 'Temperature': "100",
                 'Humidity': "100",
                 'Gas': "100",
                 'AQI': "100"},
               
              { 'Device': "100",
                'GPS': [100,2],
                'Timestamp': "100",
                'RSSI': "100",
                'Temperature': "100",
                'Humidity': "100",
                'Gas': "100",
                'AQI': "100"}]


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
    
    print(json_data)
    
    point = Point("mem") \
        .tag("Device", mac) \
        .tag("GPS", GPS) \
        .field("RSSI", rssi) \
        .field("Temperature", Temperature) \
        .field("Humidity", Humidity) \
        .field("Gas", Gas) \
        .field("AQI", AQI) \
        .time(datetime.utcnow(), WritePrecision.NS)

    #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
    write_api.write(bucket, org, point)
 
    return "ok"



#app = Flask(__name__, template_folder='templates')
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
Bootstrap(app)




# 404
@app.route('/404')
def not_found():
    abort(404)

#Main page with results
#@app.route('/')
#def index():
#    return render_template('index5.html',messages=listvalues)

@app.route('/')
def index():
    return render_template('index.html')




#https://stackoverflow.com/questions/8470431/what-is-the-best-way-to-implement-a-forced-page-refresh-using-flask
#TODO: delete
@app.route('/suggestions')
def suggestions():
    listvalues2 = []
    for i in listvalues1:
        listvalues2.append(i["Device"])
    return render_template('suggestions.html', suggestions=listvalues2)


#GET TABLES AT RUNTIME
@app.route('/tables')
def tables():

    return render_template('tables.html', messages=listvalues)







# esp32 post its value to the list listvalues
@app.route('/update-sensor/', methods=['GET', 'POST'])
def updatesensor():
    json_data = request.json
    mac = json_data["MAC"]
    GPS= json_data["GPS"]
    rssi = json_data["RSSI"]
    Temperature = json_data["Temperature"]
    Humidity = json_data["Humidity"]
    Gas = json_data["Gas"]
    AQI = json_data["AQI"]
    
    listvalues.append({'Device': mac,
                        'GPS': GPS,
                        'RSSI': rssi,
                        'Temperature': Temperature,
                        'Humidity': Humidity,
                        'Gas': Gas,
                        'AQI': AQI
                        }
                       )
    influxdb_post(json_data)

    
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
        protocol = request.form.get('comp_select')#request.form['protocol']
        if not sample_frequency:
            flash('frequency is required!'.upper())
        elif not is_int(sample_frequency):
            flash('frequency must be a number!'.upper())
        elif not min_gas_value:
            flash('min gas value is required!'.upper())
        elif not is_int(min_gas_value):
            flash('min gas value must be a number!'.upper())
        elif not max_gas_value:
            flash('max gas value is required!'.upper())
        elif not is_int(max_gas_value):
            flash('max gas value  must be a number!'.upper())
       # elif not protocol:
       #     flash('protocol is required!')
        else:
            post_parameters['sample_frequency']= sample_frequency
            post_parameters['min_gas_value']= min_gas_value
            post_parameters['max_gas_value']= max_gas_value
            post_parameters['protocol']= get_protocol(protocol)
            flash('Parameters updated')
            #return redirect(url_for('getsensor'))
            
       # select = request.form.get('comp_select')
       # print(select)


    protocols=[{'name':'HTTP'}, {'name':'COAP'}, {'name':'MQTT'}]
    return render_template('set_parameters.html',prot=protocols)






#flask run --host=0.0.0.0

#if __name__ == "__main__":
#    app.run(port = 8000,debug=True)

if __name__ == '__main__':
 #   from livereload import Server
  #  server = Server(app.wsgi_app)
  #  server.serve(host = '0.0.0.0',port=5000)
  app.run(host='0.0.0.0',port=5000)#,extra_files=listvalues)
