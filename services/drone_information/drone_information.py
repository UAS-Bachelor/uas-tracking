from flask import Flask, render_template, url_for, request, jsonify
from flask_cors import CORS
from models import db, Drone, Route
from interpolator import spline_interpolate
import time_util
import requests
import json
import sys
import argparse
import os

dirname = os.path.dirname(__file__)
__config_file = (dirname + '/' if dirname else '') + 'cfg/config.json'
config = json.load(open(__config_file))
db_config = config['db']

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}:{}/{}'.format(db_config['user'], db_config['password'], db_config['host'], db_config['port'], db_config['database'])
app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
    current_routes = result_to_list_of_dicts(db.session.query(Route.route_id, Route.drone_id, Route.start_time).filter(Route.end_time == None).order_by(Route.start_time).all())
    for route in current_routes:
        drone = result_to_dict(db.session.query(Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == route['drone_id'], Drone.time >= route['start_time']).order_by(Drone.time.desc()).first())
        current_drones.append(drone)
    return jsonify(current_drones), 200


@app.route('/live/<droneid>')
def get_live_drones_by_id(droneid):
    current_route = Route.query.filter(Route.end_time == None, Route.drone_id == droneid).order_by(Route.start_time).first()
    if not current_route:
        return jsonify(error='drone with droneid {} is currently not in flight'.format(droneid)), 404
    current_drone = result_to_dict(db.session.query(Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == current_route.drone_id, Drone.time >= current_route.start_time).order_by(Drone.time.desc()).first())
    return jsonify(current_drone), 200



    route = db.session.query(Route.drone_id, Route.start_time, Route.end_time).filter(Route.route_id == routeid).first()
    if not route:
        return jsonify(error='routeid {} does not exist'.format(routeid)), 404
    list_of_drone_dicts = result_to_list_of_dicts(db.session.query(
        Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time).all())
    return jsonify(list_of_drone_dicts), 200


@app.route('/routes', methods = ['GET', 'POST', 'DELETE'])
def routes():
    '''Returns a list of all drone routes'''
    if request.method == 'GET':
        return get_drone_routes_list()

    elif request.method == 'POST':
        return post_drone_route()

    elif request.method == 'DELETE':
        return delete_drone_route()


def get_drone_routes_list():
    list_of_drone_dicts = result_to_list_of_dicts(db.session.query(Route.route_id, Route.drone_id, Route.start_time, Route.end_time).filter(Route.end_time != None).order_by(Route.start_time).all())
    for drone_dict in list_of_drone_dicts:
        drone_dict['start_time_stamp'] = time_util.epoch_to_datetime(drone_dict['start_time'])
        drone_dict['end_time_stamp'] = time_util.epoch_to_datetime(drone_dict['end_time'])
        drone_dict['duration'] = time_util.epoch_to_time(drone_dict['end_time'] - drone_dict['start_time'])
    return jsonify(list_of_drone_dicts), 200


def post_drone_route():
    received_route = request.get_json(force=True)
    print(received_route)
    
    for received_point in received_route:
        if 'time' not in received_point:
            return jsonify(error='missing key: time'), 400
        if 'lat' not in received_point:
            return jsonify(error='missing key: lat'), 400
        if 'lon' not in received_point:
            return jsonify(error='missing key: lon'), 400
        if 'aid' in received_point:
            received_point['id'] = received_point.pop('aid')
        if 'id' not in received_point:
            received_point['id'] = 910
        if 'time_stamp' not in received_point:
            received_point['time_stamp'] = time_util.epoch_to_datetime_with_dashes(received_point['time'])
        if 'name' not in received_point:
            received_point['name'] = '{0:06d}'.format(received_point['id'])
        if 'sim' not in received_point:
            received_point['sim'] = 1
        drone_point = Drone(received_point)
        db.session.merge(drone_point)
    first_point = received_route[0]
    last_point = received_route[-1]
    route = Route.query.filter(Route.drone_id == first_point['id'], Route.start_time == first_point['time']).first()
    if route: #route already exists
        route.end_time = last_point['time']
        db.session.merge(route)
    else: #route doesn't exist
        route = Route(drone_id=first_point['id'], start_time=first_point['time'], end_time=last_point['time'])
        db.session.add(route)
    db.session.commit()
    return jsonify(route.route_id), 200


def delete_drone_route():
    received_routeid = request.get_json(force=True)['routeid']
    route_to_delete = Route.query.filter(Route.route_id == received_routeid).first()
    if not route_to_delete:
        return jsonify(error='routeid {} does not exist'.format(received_routeid)), 404
    Drone.query.filter(Drone.id == route_to_delete.drone_id, Drone.time >= route_to_delete.start_time, Drone.time <= route_to_delete.end_time).delete()
    db.session.delete(route_to_delete)
    db.session.commit()
    return jsonify(received_routeid), 200


@app.route('/routes/<routeid>')
def get_route_by_routeid(routeid):
    '''Returns list of coordinates, timestamps and drone information, for the route that corresponds to the provided route id'''
    route = Route.query.filter(Route.route_id == routeid).first()
    if not route:
        return jsonify(error='routeid {} does not exist'.format(routeid)), 404
    list_of_drone_dicts = result_to_list_of_dicts(db.session.query(
        Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time).all())
    return jsonify(list_of_drone_dicts), 200


@app.route('/routes/<routeid>/interpolated')
def get_route_by_routeid_interpolated(routeid):
    '''Returns list of interpolated (2 seconds) coordinates, timestamps and drone information, for the route that corresponds to the provided route id. Interpolation requires more than 3 coordinates.'''
    route = Route.query.filter(Route.route_id == routeid).first()
    if not route:
        return jsonify(error='routeid {} does not exist'.format(routeid)), 404
    list_of_drone_dicts = result_to_list_of_dicts(db.session.query(
        Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time).all())
    if len(list_of_drone_dicts) > 3:
        list_of_drone_dicts = spline_interpolate(list_of_drone_dicts, interpolation_interval)
    return jsonify(list_of_drone_dicts), 200


def result_to_list_of_dicts(results):
    list_of_dicts = []
    for result in results:
        list_of_dicts.append(
            dict(zip(result.keys(), result))
        )
    return list_of_dicts


def result_to_dict(result):
    return dict(zip(result.keys(), result))


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
