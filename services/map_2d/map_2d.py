from flask import Flask, render_template, url_for, request, jsonify
import requests
import sys
import json
import argparse
import time
import os


__services_config_file = os.path.join(os.path.dirname(__file__), '../../cfg/services.json')
config = json.load(open(__services_config_file))

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/')
def index():
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@app.route('/live')
def get_2d_live_map():
    '''Returns a 2D map'''
    if not request.is_json:
        return jsonify(error='missing resource data'), 400
    data = request.get_json(force=True)
    live_drones_url = data['live']
    kml_url = data['no_fly_zones']
    return render_template('map.html', kml_url=kml_url, live_drones_url=live_drones_url)


@app.route('/routes')
def get_2d_map():
    '''Returns a 2D map with a route drawn on it, that corresponds to the provided route id'''
    if not request.is_json:
        return jsonify(error='missing resource data'), 400
    data = request.get_json(force=True)
    kml_url = data['no_fly_zones']
    drone_route_list = data['drone_route_list']
    route_duration = -1
    if all(route for route in drone_route_list):
        route_duration = epoch_to_time(drone_route_list[-1]['time'] - drone_route_list[0]['time'])
    return render_template('map.html', drone_route_list=drone_route_list, route_duration=route_duration, kml_url=kml_url)


def epoch_to_time(epoch):
    return time.strftime('%H:%M:%S', time.gmtime(epoch))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='0.0.0.0',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5002,
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
