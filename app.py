from flask import Flask, render_template, url_for
import requests

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map():
    return requests.get('http://127.0.0.1:5001/map').content

if __name__ == '__main__':
    app.run(debug=True)
