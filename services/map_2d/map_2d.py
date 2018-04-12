from flask import Flask, render_template, url_for, request, jsonify
import requests
import sys
import json
import argparse
import time
import os

app = Flask(__name__)
app.url_map.strict_slashes = False

__services_config_file = os.path.realpath(__file__) + '/../../../cfg/services.json'
config = json.load(open(__services_config_file))


@app.route('/')
def index():
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@app.route('/map2d')
def get_2d_map():
    '''Returns a 2D map'''
    return render_template('map.html')


@app.route('/routes/<routeid>/2d')
def get_2d_map_by_routeid(routeid):
    '''Returns a 2D map with a route drawn on it, that corresponds to the provided route id'''
    try:
        route_config = config['drone_information']
        request.path = '/routes/{}/interpolated'.format(routeid)
        drone_route_list = json.loads(__get_url(route_config))
        route_duration = -1
        if all(route for route in drone_route_list):
            route_duration = epoch_to_time(drone_route_list[-1]['time'] - drone_route_list[0]['time'])
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable'
    return render_template('map.html', drone_route_list=drone_route_list, route_duration=route_duration)


def epoch_to_time(epoch):
    return time.strftime('%H:%M:%S', time.gmtime(epoch))


def __get_url(route_config):
    if(request.remote_addr == '127.0.0.1'):
        return requests.get('http://127.0.0.1:{}{}'.format(route_config['port'], request.path)).text
    else:
        return requests.get('http://{}:{}{}'.format(route_config['host'], route_config['port'], request.path)).text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5002,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=True, threaded=True)
