from flask import Flask, render_template, url_for, request, json
import requests
import sys
import argparse
from os import system

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map3d')
def map_3d():
    try:
        map = requests.get('http://10.126.29.182:5001/map').text
    except requests.exceptions.ConnectionError:
        return '3D Map service unavailable'
    return render_template('layout.html', html=map)


@app.route('/map2d')
def map_2d():
    try:
        map = requests.get('http://192.168.93.1:5004/map').text
    except requests.exceptions.ConnectionError:
        return '2D Map service unavailable'
    return render_template('layout.html', html=map)


@app.route('/list')
def list():
    try:
        drone_list = json.loads(requests.get('http://192.168.93.1:5005/list').text)
        names = ""
        for name in drone_list:
            names += name + "\r\n"
        #drone_list = requests.get('http://192.168.93.1:5005/list').text
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable'
    return names


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=False)
