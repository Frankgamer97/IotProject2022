
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

post_parameters = {'sample_frequency': "5000",
             'min_gas_value': "0",
             'max_gas_value': "100",
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
    return "ok"

#esp32 take values from the json post_parameters
@app.route("/get-sensor/", methods=('GET', 'POST'))
def getsensor():
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
        protocol = request.form['protocol']
        if not sample_frequency:
            flash('sample_frequency is required!')
        elif not min_gas_value:
            flash('min_gas_value is required!')
        elif not max_gas_value:
            flash('max_gas_value is required!')
        elif not protocol:
            flash('protocol is required!')
        else:
            post_parameters['sample_frequency']= sample_frequency
            post_parameters['min_gas_value']= min_gas_value
            post_parameters['max_gas_value']= max_gas_value
            post_parameters['protocol']= protocol
            flash('Parameters updated')
            #return redirect(url_for('getsensor'))

    return render_template('set_parameters.html')






#flask run --host=0.0.0.0

#if __name__ == "__main__":
#    app.run(port = 8000,debug=True)

if __name__ == '__main__':
 #   from livereload import Server
  #  server = Server(app.wsgi_app)
  #  server.serve(host = '0.0.0.0',port=5000)
  app.run(host='0.0.0.0',port=5000)#,extra_files=listvalues)
