from flask import Flask, render_template, url_for, request
import requests
import sys
import argparse
from os import system

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
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='specity which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    system('title {} service version {} on port {}'.format(
        args.prog, args.version, args.port))
    app.run(port=args.port, debug=True)
