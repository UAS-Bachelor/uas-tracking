from flask import Flask, render_template, url_for, request
import requests
import os
import sys
import argparse

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map')
def map():
    try:
        map = requests.get('http://127.0.0.1:5001/map').content
    except requests.exceptions.ConnectionError:
        return 'Map service unavailable'
    return map


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        login = requests.get('http://127.0.0.1:5002/login').content
    except requests.exceptions.ConnectionError:
        return 'Login service unavailable'
    return login

 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help='specity which port to run this service on')
    args = parser.parse_args()

    print('Running {} service'.format(sys.argv[0].split('.')[0]))
    app.run(port=args.port, debug=True)
