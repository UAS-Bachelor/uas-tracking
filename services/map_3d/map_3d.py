from flask import Flask, render_template, url_for, request, jsonify
from flask_cors import CORS
import requests
import json
import sys
import argparse
import os


__services_config_file = os.path.join(os.path.dirname(__file__), '../../cfg/services.json')
config = json.load(open(__services_config_file))

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)


@app.route('/')
def index():
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@app.route('/map3d')
def get_3d_map():
    '''Returns a 3D map'''
    try:
        kml_url = get_url_string('no_fly_information', '/zones')
    except requests.exceptions.ConnectionError:
        return 'No fly information service unavailable'
    return render_template('map.html', kml_url=kml_url)


@app.route('/routes/<routeid>/3d')
def get_3d_map_by_routeid(routeid):
    '''Returns a 3D map with a route drawn on it, that corresponds to the provided route id'''
    try:
        drone_route_list = json.loads(get('drone_information', '/routes/{}'.format(routeid)))
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable', 503
    return render_template('map.html', drone_route_list=drone_route_list)


def get(service_name, path=request.path):
    url = get_url_string(service_name, path)
    response = requests.get(url)
    raise_for_status_code(response)
    return response.text


def get_url_string(service_name, path=request.path):
    service_config = config[service_name]
    url = 'http://{}:{}{}'
    if(request.remote_addr == '127.0.0.1'):
        url = url.format('127.0.0.1', service_config['port'], path)
    else:
        url = url.format(service_config['host'], service_config['port'], path)
    return url


def raise_for_status_code(response):
    if not response:
        exception = requests.exceptions.HTTPError(response.status_code, response.reason)
        exception.text = response.text
        raise exception


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='0.0.0.0',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5003,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='run this service in debug mode')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=args.debug, threaded=True)
