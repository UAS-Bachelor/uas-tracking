from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import sys
import argparse
from configobj import ConfigObj
from os import system

__services_config = 'cfg/dbconfig.ini'
configobj = ConfigObj(__services_config)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + configobj['user'] + ':' + configobj['password'] + '@' + configobj['host'] + '/' + configobj['database']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Drone(db.Model):
    time_stamp = db.Column(db.String(255))
    time = db.Column(db.BigInteger(), primary_key=True)
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(20))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    alt = db.Column(db.Float)
    acc = db.Column(db.Float)
    fix = db.Column(db.SmallInteger)
    lnk = db.Column(db.SmallInteger)
    eng = db.Column(db.SmallInteger)
    sim = db.Column(db.SmallInteger)

    def __init__(self, time_stamp, time, id, name, lat, lon, alt, acc, fix, lnk, eng, sim):
        self.time_stamp = time_stamp
        self.time = time
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.acc = acc
        self.fix = fix
        self.lnk = lnk
        self.eng = eng
        self.sim = sim


drone = Drone('ts', 1, 'id', 'name', 55, 10, 20, 15, 1, 2, 100, 1)
db.session.add(drone)
db.session.commit()


def get_drone_info():
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
    return list_of_drone_dicts

@app.route('/list')
def list():
    drone_names = [drone_data['name'] for drone_data in get_drone_info()]
    print(drone_names)
    return jsonify(drone_names)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5005,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=True)
