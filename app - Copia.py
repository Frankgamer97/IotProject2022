
# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os,requests
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from markupsafe import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, flash, session, jsonify, render_template
from flask_bootstrap import Bootstrap


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


messages = [{'sample_frequency': '10000',
             'min_gas_value': '0',
             'max_gas_value':'100'}
            ]

lista=[0]
def generator_lista():
    return lista[-1]

def values():
    value =generator_lista()
    return '''
<h1>ESP32 SERVER</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % value

#app = Flask(__name__, template_folder='templates')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
Bootstrap(app)


# get name value from query string and cookie
#@app.route('/')
#def index():
#    return render_template('index.html')



@app.route('/hello')
def hello():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % escape(name)  # escape name to avoid XSS
    # return different response according to the user's authentication status
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response


# redirect
@app.route('/hi')
def hi():
    return redirect(url_for('hello'))


# use int URL converter
@app.route('/goback/<int:year>')
def go_back(year):
    return 'Welcome to %d!' % (2018 - year)


# use any URL converter
@app.route('/colors/<any(blue, white, red):color>')
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or proud or rude.</p>'


# return error response
@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(418)
    else:
        return 'A drop of tea.'


# 404
@app.route('/404')
def not_found():
    abort(404)


# return response with different formats
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''Note
to: Peter
from: Jane
heading: Reminder
body: Don't forget the party!
'''
        response = make_response(body)
        response.mimetype = 'text/plain'
    elif content_type == 'html':
        body = '''<!DOCTYPE html>
<html>
<head></head>
<body>
  <h1>Note</h1>
  <p>to: Peter</p>
  <p>from: Jane</p>
  <p>heading: Reminder</p>
  <p>body: <strong>Don't forget the party!</strong></p>
</body>
</html>
'''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'xml':
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<note>
  <to>Peter</to>
  <from>Jane</from>
  <heading>Reminder</heading>
  <body>Don't forget the party!</body>
</note>
'''
        response = make_response(body)
        response.mimetype = 'application/xml'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        response = jsonify(body)
        # equal to:
        # response = make_response(json.dumps(body))
        # response.mimetype = "application/json"
    else:
        abort(400)
    return response


# set cookie
@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hello')))
    response.set_cookie('name', name)
    return response


# log in user
@app.route('/login')
def login():
    session['logged_in'] = True
    return redirect(url_for('hello'))


# protect view
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return 'Welcome to admin page.'


# log out user
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hello'))


# AJAX
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


# redirect to last page
@app.route('/foo')
def foo():
    return '<h1>Foo page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/bar')
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/do-something')
def do_something():
    # do something here
    return redirect_back()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


#@app.route('/update-sensor', methods=['GET', 'POST'])
#def starting_url():
#    json_data = request.json
#    a_value = json_data["MAC"]
#    lista.append(a_value)
#
#    return values()







@app.route('/')
def index():
    return render_template('index3.html', messages=listvalues)



@app.route('/base')
def base():
    return render_template('base.html', messages=listvalues)






@app.route("/get-sensor/", methods=('GET', 'POST'))
def getsensor():
    return jsonify(
        sample_frequency=post_parameters["sample_frequency"],
        min_gas_value=post_parameters["min_gas_value"],
        max_gas_value=post_parameters["max_gas_value"],
        protocol=post_parameters["protocol"],
    )


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







@app.route('/update-sensor/', methods=['GET', 'POST'])
def starting_url():
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
            


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        sample_frequency= request.form['sample_frequency']
        min_gas_value = request.form['min_gas_value']
        max_gas_value = request.form['max_gas_value']

        if not sample_frequency:
            flash('sample_frequency is required!')
        elif not min_gas_value:
            flash('Content is required!')
        elif not max_gas_value:
            flash('Content is required!')
        else:
            messages.append({'sample_frequency': sample_frequency, 'min_gas_value': min_gas_value, 'max_gas_value': max_gas_value})
            return redirect(url_for('index'))

    return render_template('create.html')




# AJAX
@app.route('/postino')
def postino():
    return values()


@app.route('/temp', methods =['GET'])
def home():
    #construct_url = "https://api.openweathermap.org/data/2.5/weather?q=London&appid=" + "your api key goes here"
    #response = requests.get(construct_url)

    list_of_data = {"country":"London","temp":30,"hum":50}#response.json()
    
    html_data = f"""
    <table border="1">
    <tr>
        <td>country_code</td>
        <td>temp</td>
        <td>humidity</td>
    </tr>
    <tr>
        <td>{str(list_of_data['country'])}</td>

        <td>{str(list_of_data['temp']) + 'c'}</td>
        <td>{str(list_of_data['hum'])}</td>
    </tr>

</table>
    """
    return html_data

#if __name__ == "__main__":
#    app.run(port = 8000,debug=True)

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
