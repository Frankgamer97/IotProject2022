import os
from markupsafe import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, session, jsonify, render_template
from flask_bootstrap import Bootstrap


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

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
Bootstrap(app)


# get name value from query string and cookie
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update-sensor', methods=['POST'])
def starting_url():
    json_data = request.json
    a_value = json_data["sensor"]
    lista.append(a_value)

    return values()



# AJAX
@app.route('/postino', methods=['GET'])
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

