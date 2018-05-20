from flask import Flask, url_for, redirect, jsonify, request
from flask_cors import CORS
from scripts.get_no_fly_zones import download
from fastkml import kml
from pygeoif import MultiPolygon
from haversine import haversine
import requests
import json
import argparse
import sys
import os
import time
import math


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app)

__services_config_file = os.path.join(os.path.dirname(__file__), '../../cfg/services.json')
config = json.load(open(__services_config_file))

features = None


@app.route('/')
def index():
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@app.route('/zones')
def get_nofly_zones_list():
    return redirect(url_for('static', filename='kml/drone_no_fly_dk.kml', _external=True))


@app.route('/collision/zones/<droneid>')
def get_zone_collisions_by_droneid(droneid):
    try:
        drone = json.loads(get('drone_information', '/live/{}'.format(droneid)))
        inside = drone_in_zone(drone['lon'], drone['lat'])
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable', 503
    try:
        return jsonify(inside=inside is not None, zone=inside.name), 200
    except AttributeError:
        return jsonify(inside=inside is not None, zone=None), 200


@app.route('/collision/drones')
def get_live_collisions():
    try:
        current_drones = json.loads(get('drone_information', '/live'))
        dict_of_colliding_drones = {}
        for drone in current_drones:
            dict_of_colliding_drones = {**dict_of_colliding_drones, **drone_in_drone(drone, current_drones)}
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable', 503
    return jsonify(dict_of_colliding_drones), 200


@app.route('/collision/drones/<droneid>')
def get_live_collisions_by_droneid(droneid):
    try:
        drone = json.loads(get('drone_information', '/live/{}'.format(droneid)))
        current_drones = json.loads(get('drone_information', '/live'))
        dict_of_colliding_drones = drone_in_drone(drone, current_drones)
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable', 503
    return jsonify(dict_of_colliding_drones), 200


def drone_in_drone(drone, list_of_current_drones):
    dict_of_colliding_drones = {}
    for current_drone in list_of_current_drones:
        if(drone['id'] != current_drone['id']):
            if get_distance_between_drone_points(drone, current_drone) < drone['buffer_radius']: 
                if drone['id'] not in dict_of_colliding_drones:
                    dict_of_colliding_drones[drone['id']] = []
                dict_of_colliding_drones[drone['id']].append({
                        'id': current_drone['id'], 
                        'distance' : get_distance_between_drone_points(drone, current_drone)
                    })
    return dict_of_colliding_drones


def get_distance_between_drone_points(drone1, drone2):
    return round(haversine((drone1['lat'], drone1['lon']), (drone2['lat'], drone2['lon'])) * 1000, 2)


def drone_in_zone(x= 12.39, y= 55.85, z=0):# to get inside = True
    for feature in features:
        try:
            feature_geometry = feature.geometry
            inside = point_in_polygon(x, y, z, feature_geometry.exterior.coords)
        except AttributeError: #to handle multi-polygons
            for geometry in feature_geometry.geoms:
                inside = point_in_polygon(x, y, z, geometry.exterior.coords)
        if inside:
            print('Drone is in {}'.format(feature.name))
            return feature
    return None


def point_in_polygon(x, y, z, polygon):
    inside = False
    p1x, p1y, p1z = polygon[-1]

    for i in range(len(polygon)):
        p2x, p2y, p2z = polygon[i]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if z <= max(p1z, p2z):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
        p1x, p1y, p1z = p2x, p2y, p2z
    return inside


def get(service_name, path=''):
    url = get_url_string(service_name, path)
    response = requests.get(url)
    raise_for_status_code(response)
    return response.text


def get_url_string(service_name, path=''):
    if request and path == '':
        path = request.path
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


def load_file(file_name):
    kml_file = kml.KML()

    kml_file.from_string(open(file_name, 'rb').read())
    global features
    features = list(list(kml_file.features())[0].features())


def prepare_file():
    print('Locating KML file')
    directory = os.path.join(os.path.dirname(__file__), 'static/kml/')
    file_name = os.path.join(directory, 'drone_no_fly_dk.kml')
    if os.path.isfile(file_name):
        seven_days_in_seconds = 7 * 24 * 60 * 60
        if (int(time.time()) - int(os.path.getmtime(file_name))) > seven_days_in_seconds:
            print('KML file older than seven days, downloading new')
            download()
        print('Attempting to read KML file')
        load_file(file_name)
    else:
        print('KML file not found, attempting to download')
        download()
        load_file(file_name)
    print('KML file read')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='0.0.0.0',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5004,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='run this service in debug mode')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    prepare_file()
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=args.debug, threaded=True)
