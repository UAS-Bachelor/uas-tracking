from flask import Flask, render_template, url_for, request, json
import requests
from configobj import ConfigObj
import sys
import argparse
import os

app = Flask(__name__)

__services_config = os.path.realpath(__file__) + '/../../../services.ini'
configobj = ConfigObj(__services_config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map3d')
def map_3d():
    try:
        cfg = configobj['map_3d']
        #map3 = requests.get('http://192.168.93.1:5001/map').text
        map3d = requests.get('http://{}:{}/map'.format(cfg['host'], cfg['port'])).text
    except requests.exceptions.ConnectionError:
        return '3D Map service unavailable'
    return render_template('layout.html', html=map3d)


# called like localhost:5000/map2d?id=000910&start_time=1500&end_time=2000
@app.route('/map2d')
def map_2d():
    '''id = request.args.get('id')
    start_time = request.args.get('start')
    end_time = request.args.get('end')'''
    try:
        cfg = configobj['map_2d']
        map2d = requests.get('http://{}:{}/map2d'.format(cfg['host'], cfg['port'])).text
    except requests.exceptions.ConnectionError:
        return '2D Map service unavailable'
    return render_template('layout.html', html=map2d)


@app.route('/map2d/<id>/<start_time>/<end_time>')
def map_2d_with_params(id, start_time, end_time):
    try:
        cfg = configobj['map_2d']
        map2d = requests.get('http://{}:{}/map2d/{}/{}/{}'.format(cfg['host'], cfg['port'], id, start_time, end_time)).text
    except requests.exceptions.ConnectionError:
        return '2D Map service unavailable'
    return render_template('layout.html', html=map2d)


@app.route('/list')
def list_drones():
    try:
        cfg = configobj['drone_information']
        drone_list = json.loads(requests.get('http://{}:{}/list'.format(cfg['host'], cfg['port'])).text)
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable'
    return render_template('list.html', drones=drone_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='0.0.0.0',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    #app.run(host=args.address, port=args.port, debug=True)
    app.run(host=args.address, port=args.port, debug=False)
