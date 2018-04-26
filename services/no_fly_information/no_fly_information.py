from flask import Flask, url_for, redirect, jsonify
from flask_cors import CORS
from scripts.get_no_fly_zones import download
from fastkml import kml
from pygeoif import MultiPolygon
import argparse
import sys
import os
import time


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

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


@app.route('/conflicts')
def get_conflicts():
    drone_in_zone()
    return ''


def drone_in_zone():
    x = 14.939
    y = 55.029
    z = 1
    start = time.time()
    i = 0
    for f in features:
        try:
            inside = point_in_polygon(x, y, z, f.geometry.exterior.coords)
        except AttributeError:
            print('Found multipoly')
            for geom in f.geometry.geoms:
                print('looping through polygons in multipoly')
                inside = point_in_polygon(x, y, z, geom.exterior.coords)
        i = i + 1
        if inside:
            break
    print('Done, took {}'.format(time.time() - start))
    print('index: {}'.format(i))


def point_in_polygon(x, y, z, polygon):
    n = len(polygon)
    inside = False
    p1x, p1y, p1z = polygon[0]

    for i in range(n + 1):
        p2x, p2y, p2z = polygon[i % n]
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


def load_file(file_name):
    kml_file = kml.KML()

    kml_file.from_string(open(file_name, 'rb').read())
    global features
    features = list(list(kml_file.features())[0].features())


def prepare_file():
    print('Locating KML file')
    dirname = os.path.dirname(__file__)
    directory = (dirname + '/' if dirname else '') + 'static/kml/'
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
