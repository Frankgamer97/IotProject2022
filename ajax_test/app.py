from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('test_suggestions.html')


@app.route('/suggestions')
def suggestions():
    text = request.args.get('jsdata')

    suggestions_list = []

    if text:
        r = requests.get('http://suggestqueries.google.com/complete/search?output=toolbar&hl=ru&q={}&gl=in'.format(text))

        soup = BeautifulSoup(r.content, 'lxml')

        suggestions = soup.find_all('suggestion')

        for suggestion in suggestions:
            suggestions_list.append(suggestion.attrs['data'])

        #print(suggestions_list)

    return render_template('suggestions.html', suggestions=suggestions_list)


if __name__ == '__main__':
    app.run(debug=True)
