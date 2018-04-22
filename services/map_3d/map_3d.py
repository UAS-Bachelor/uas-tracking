from flask import Flask, render_template, url_for, request, jsonify
from flask_cors import CORS
import requests
import json
import sys
import argparse
import os

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

dirname = os.path.dirname(__file__)
__services_config_file = (dirname + '/' if dirname else '') + '../../cfg/services.json'
config = json.load(open(__services_config_file))


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
    return render_template('map.html')


@app.route('/routes/<routeid>/3d')
def get_3d_map_by_routeid(routeid):
    '''Returns a 3D map with a route drawn on it, that corresponds to the provided route id'''
    try:
        route_config = config['drone_information']
        request.path = '/routes/{}'.format(routeid)
        drone_route_list = json.loads(get(route_config))
    except requests.exceptions.HTTPError as exception:
        return exception.text, exception.errno
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable', 503
    return render_template('map.html', drone_route_list=drone_route_list)


def get(route_config):
    url = 'http://{}:{}{}'
    if(request.remote_addr == '127.0.0.1'):
        url = url.format('127.0.0.1', route_config['port'], request.path)
    else:
        url = url.format(route_config['host'], route_config['port'], request.path)
    response = requests.get(url)
    raise_for_status_code(response)
    return response.text


def raise_for_status_code(response):
    if not response:
        exception = requests.exceptions.HTTPError(response.status_code, response.reason)
        exception.text = response.text
        raise exception


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5003,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=True, threaded=True)
