from flask import Flask, render_template, url_for, request, jsonify, abort
from flask_cors import CORS
import sys
import argparse
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from database_driver import DatabaseDriver, Drone, Route
from interpolator import spline_interpolate
from time_util import epoch_to_datetime, epoch_to_datetime_with_dashes, epoch_to_time
import exceptions


__config_file = os.path.join(os.path.dirname(__file__), 'cfg/config.json')
config = json.load(open(__config_file))
db_config = config['db']

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app)

db = DatabaseDriver(app, db_config)

interpolation_interval = config['interpolation_interval']


@app.route('/')
def index():
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@app.route('/live')
def get_live_drones():
    current_drones = []
    current_routes = db.get_live_routes()
    for route in current_routes:
        drone = db.get_data_point_by_live_route(route)
        drone['buffer_radius'] = 500
        current_drones.append(drone)
    return jsonify(current_drones), 200


@app.route('/live/<droneid>')
def get_live_drone_by_id(droneid):
    current_route = db.get_latest_live_route_by_droneid(droneid)
    if not current_route:
        return jsonify(error='drone with droneid {} is currently not in flight'.format(droneid)), 404
    current_drone = db.get_data_point_by_live_route(current_route)
    current_drone['buffer_radius'] = 500
    return jsonify(current_drone), 200


@app.route('/routes', methods = ['GET', 'POST'])
def routes():
    if request.method == 'GET':
        return get_drone_routes()

    elif request.method == 'POST':
        return post_drone_route()


def get_drone_routes():
    list_of_drone_dicts = db.get_finished_routes()
    for drone_dict in list_of_drone_dicts:
        drone_dict['start_time_stamp'] = epoch_to_datetime(drone_dict['start_time'])
        drone_dict['end_time_stamp'] = epoch_to_datetime(drone_dict['end_time'])
        drone_dict['duration'] = epoch_to_time(drone_dict['end_time'] - drone_dict['start_time'])
    return jsonify(list_of_drone_dicts)


def post_drone_route():
    received_route = request.get_json(force=True)
    print(received_route)
    try:
        for drone_data_point in received_route:
            __fit_drone_data_point(drone_data_point)
        first_point = received_route[0]
        last_point = received_route[-1]
        route = db.get_route_by_droneid_and_start_time(first_point['id'], first_point['time'])
        if route: #route already exists
            db.delete_data_points_by_route(route)
            route.end_time = last_point['time']
        else: #route doesn't exist
            route = Route(drone_id=first_point['id'], start_time=first_point['time'], end_time=last_point['time'])
        for drone_data_point in received_route:
            drone_point = Drone(drone_data_point)
            db.merge(drone_point)
        db.add(route)
        db.commit()
    except exceptions.MissingKeyException as exception:
        return jsonify(error=exception.text), exception.status_code
    return jsonify(route.route_id), 201


def put_drone_route(routeid):
    received_route = request.get_json(force=True)
    print(received_route)
    try:
        for drone_data_point in received_route:
            __fit_drone_data_point(drone_data_point)
            drone_point = Drone(drone_data_point)
            db.merge(drone_point)
        first_point = received_route[0]
        last_point = received_route[-1]
        route = db.get_route_by_routeid(routeid)
        if route and route.drone_id == int(first_point['id']):
            route.start_time = first_point['time']
            route.end_time = last_point['time']
            db.merge(route)
            db.commit()
        else:
            db.rollback()
            raise exceptions.RouteNotFoundException('route_id: {}, drone_id: {}'.format(routeid, first_point['id']))
    except (exceptions.MissingKeyException, exceptions.RouteNotFoundException) as exception:
        return jsonify(error=exception.text), exception.status_code
    return jsonify(route.route_id), 200


def __fit_drone_data_point(drone_data_point):
    if 'time' not in drone_data_point:
        raise exceptions.MissingKeyException('time')
    if 'lat' not in drone_data_point:
        raise exceptions.MissingKeyException('lat')
    if 'lon' not in drone_data_point:
        raise exceptions.MissingKeyException('lon')
    if 'alt' not in drone_data_point:
        raise exceptions.MissingKeyException('alt')
    if 'aid' in drone_data_point:
        drone_data_point['id'] = drone_data_point.pop('aid')
    if 'id' not in drone_data_point:
        drone_data_point['id'] = 910
    if 'time_stamp' not in drone_data_point:
        drone_data_point['time_stamp'] = epoch_to_datetime_with_dashes(drone_data_point['time'])
    if 'name' not in drone_data_point:
        drone_data_point['name'] = '{0:06d}'.format(drone_data_point['id'])
    if 'sim' not in drone_data_point:
        drone_data_point['sim'] = 1
    return drone_data_point


@app.route('/routes/<routeid>', methods = ['GET', 'PUT', 'DELETE'])
def route_by_routeid(routeid):
    if request.method == 'GET':
        return get_route_points_by_routeid(routeid)

    elif request.method == 'PUT':
        return put_drone_route(routeid)

    elif request.method == 'DELETE':
        return delete_route_by_routeid(routeid)


def get_route_points_by_routeid(routeid):
    '''Returns list of coordinates, timestamps and drone information, for the route that corresponds to the provided route id'''
    try:
        route = db.get_route_by_routeid(routeid)
    except exceptions.RouteNotFoundException as exception:
        return jsonify(error=exception.text), 404
    list_of_drone_dicts = db.get_data_points_by_route(route)
    return jsonify(list_of_drone_dicts), 200


def delete_route_by_routeid(routeid):
    try:
        route_to_delete = db.get_route_by_routeid(routeid)
        delete_route_and_data_points(route_to_delete)
    except exceptions.RouteNotFoundException as exception:
        return jsonify(error=exception.text), 404
    return jsonify(int(routeid)), 200


def delete_route_and_data_points(route_to_delete):
    db.delete_data_points_by_route(route_to_delete)
    db.delete(route_to_delete)
    db.commit()


@app.route('/routes/<routeid>/interpolated')
def get_route_by_routeid_interpolated(routeid):
    '''Returns list of interpolated (2 seconds) coordinates, timestamps and drone information, for the route that corresponds to the provided route id. Interpolation requires more than 3 coordinates.'''
    try:
        route = db.get_route_by_routeid(routeid)
    except exceptions.RouteNotFoundException as exception:
        return jsonify(error=exception.text), 404
    list_of_drone_dicts = db.get_data_points_by_route(route)
    if len(list_of_drone_dicts) > 3:
        list_of_drone_dicts = spline_interpolate(list_of_drone_dicts, interpolation_interval)
    return jsonify(list_of_drone_dicts), 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='0.0.0.0',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5001,
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
