from flask import Flask, render_template, url_for, request, jsonify
from models import *
import requests
import sys
import argparse
import time
from scipy import interpolate
from configobj import ConfigObj
import os

__services_config = os.path.realpath(__file__) + '/../cfg/dbconfig.ini'
configobj = ConfigObj(__services_config)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + configobj['user'] + ':' + configobj['password'] + '@' + configobj['host'] + ':' + configobj['port'] + '/' + configobj['database']
app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

interpolation_interval = 2

#SELECT * FROM routes_end
#routes_end, for så får vi de ruter der ER færdige
'''def get_drone_info():
    list_of_drone_dicts = []
    drone_info = requests.get('https://droneid.dk/bsc2018/droneid.php').text.strip('\n')
    if drone_info:
        for row in drone_info.splitlines():
            data = row.split(',')
            list_of_drone_dicts.append({
                'time_stamp': data[0],
                'time': data[1], 
                'id': data[2], 
                'name': data[3], 
                'lat': data[4],
                'lon': data[5], 
                'alt': data[6], 
                'acc': data[7], 
                'fix': data[8], 
                'lnk': data[9], 
                'eng': data[10], 
                'sim': data[11]
            })
    return list_of_drone_dicts'''

@app.route('/list')
def list_drones():
    #drone = db.session.query(Drone.lon).filter_by(id='501').filter(Drone.time >= 1521712566, Drone.time <= 1521712581).all()
    #drone = db.session.query(Route_end.id, Route_end.end_time).all()
    #userList = users.query.join(friendships, users.id==friendships.user_id).add_columns(users.userId, users.name, users.email, friends.userId, friendId).filter(users.id == friendships.friend_id).filter(friendships.user_id == userID).paginate(page, 1, False)
    #drone_routes = Route_end.query.join(Route_start, Route_end.id==Route_start.id).add_columns(Route_start.start_time).all()
    
    #drone_routes_results = db.session.query(Route_end.id, Route_end.end_time).join(Route_start, Route_end.id==Route_start.id).add_columns(Route_start.start_time).all()
    list_of_drone_dicts = result_to_list_of_dicts(db.session.query(Route.route_id, Route.drone_id.label('id'), Route.start_time, Route.end_time).filter(Route.end_time != None).all())
    
    for drone_dict in list_of_drone_dicts:
        drone_dict['start_time_stamp'] = epoch_to_datetime(drone_dict['start_time'])
        drone_dict['end_time_stamp'] = epoch_to_datetime(drone_dict['end_time'])
        drone_dict['duration'] = epoch_to_time(drone_dict['end_time'] - drone_dict['start_time'])
    return jsonify(list_of_drone_dicts)


@app.route('/<id>/<start_time>/<end_time>')
def route_with_params(id, start_time, end_time):
    list_of_drone_dicts = result_to_list_of_dicts(db.session.query(Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon).filter(Drone.id == id, Drone.time >= start_time, Drone.time <= end_time).all())
    if len(list_of_drone_dicts) > 3:
        list_of_drone_dicts = spline_interpolate(list_of_drone_dicts, interpolation_interval)
    return jsonify(list_of_drone_dicts)


def spline_interpolate(drone_route_list, interval):
    interpolated_result = []
    drone = drone_route_list[0]
    time = [drone_route['time'] for drone_route in drone_route_list]
    lat = [drone_route['lat'] for drone_route in drone_route_list]
    lon = [drone_route['lon'] for drone_route in drone_route_list]
    counter = time[0]
    end_time = time[-1]
    lat_tck = interpolate.splrep(time, lat) #cubic spline interpolation requires >3 data points
    lon_tck = interpolate.splrep(time, lon)

    while counter <= end_time:
        interpolated_lat = interpolate.splev(counter, lat_tck).tolist()
        interpolated_lon = interpolate.splev(counter, lon_tck).tolist()

        interpolated_result.append({
            'time_stamp': epoch_to_time(counter),
            'time': counter,
            'id': drone['id'],
            'lat': interpolated_lat,
            'lon': interpolated_lon
        })
        counter += interval
    return interpolated_result


def result_to_list_of_dicts(results):
    list_of_dicts = []
    for result in results:
        list_of_dicts.append(
            dict(zip(result.keys(), result))
        )
    return list_of_dicts


def epoch_to_datetime(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))


def epoch_to_time(epoch):
    return time.strftime('%H:%M:%S', time.gmtime(epoch))


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
