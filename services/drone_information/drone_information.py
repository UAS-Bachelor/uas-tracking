from flask import Flask, render_template, url_for, request, jsonify
from models import db, Drone, Route
from interpolator import spline_interpolate
import time_util
import requests
import json
import sys
import argparse
import os

__config_file = os.path.realpath(__file__) + '/../cfg/config.json'
config = json.load(open(__config_file))
db_config = config['db']

app = Flask(__name__)
app.url_map.strict_slashes = False

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


@app.route('/routes', methods = ['GET', 'POST'])
def routes():
    '''Returns a list of all drone routes'''
    if request.method == 'GET':
        return get_drone_routes_list()

    if request.method == 'POST':
        return post_drone_route()


def get_drone_routes_list():
    list_of_drone_dicts = result_to_list_of_dicts(db.session.query(Route.route_id, Route.drone_id, Route.start_time, Route.end_time).filter(Route.end_time != None).all())
    for drone_dict in list_of_drone_dicts:
        drone_dict['start_time_stamp'] = time_util.epoch_to_datetime(drone_dict['start_time'])
        drone_dict['end_time_stamp'] = time_util.epoch_to_datetime(drone_dict['end_time'])
        drone_dict['duration'] = time_util.epoch_to_time(drone_dict['end_time'] - drone_dict['start_time'])
    return jsonify(list_of_drone_dicts)


def post_drone_route():
    print(request.json)
    received_route = request.get_json(force=True)
    print(received_route)
    
    for received_point in received_route:
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
    route = Route(drone_id=first_point['id'], start_time=first_point['time'], end_time=last_point['time'])
    db.session.merge(route)
    db.session.commit()
    return ''


@app.route('/routes/<routeid>')
def get_route_by_routeid(routeid):
    '''Returns list of coordinates, timestamps and drone information, for the route that corresponds to the provided route id'''
    route = db.session.query(Route.drone_id, Route.start_time, Route.end_time).filter(Route.route_id == routeid).first()
    list_of_drone_dicts = [{}]
    if(route):
        list_of_drone_dicts = result_to_list_of_dicts(db.session.query(
            Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time).all())
    return jsonify(list_of_drone_dicts)


@app.route('/routes/<routeid>/interpolated')
def get_route_by_routeid_interpolated(routeid):
    '''Returns list of interpolated (2 seconds) coordinates, timestamps and drone information, for the route that corresponds to the provided route id. Interpolation requires more than 3 coordinates.'''
    route = db.session.query(Route.drone_id, Route.start_time, Route.end_time).filter(Route.route_id == routeid).first()
    list_of_drone_dicts = [{}]
    if(route):
        list_of_drone_dicts = result_to_list_of_dicts(db.session.query(
            Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time).all())
        if len(list_of_drone_dicts) > 3:
            list_of_drone_dicts = spline_interpolate(list_of_drone_dicts, interpolation_interval)
    return jsonify(list_of_drone_dicts)


def result_to_list_of_dicts(results):
    list_of_dicts = []
    for result in results:
        list_of_dicts.append(
            dict(zip(result.keys(), result))
        )
    return list_of_dicts


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5001,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=True, threaded=True)
