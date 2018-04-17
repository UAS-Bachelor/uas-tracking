from flask import Flask, url_for, redirect, jsonify
from flask_cors import CORS
from fastkml import kml
from pygeoif import MultiPolygon
import argparse
import sys
import os
import datetime


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
    return redirect(url_for('static', filename='drone_nofly_dk.kml', _external=True))


@app.route('/conflicts')
def get_conflicts():
    drone_in_zone()
    return ''


def drone_in_zone():
    x = 14.939
    y = 55.029
    start = datetime.datetime.now()
    i = 0
    for f in features:
        try:
            inside = point_in_polygon(x, y, f.geometry.exterior.coords)
        except AttributeError:
            print('Found multipoly')
            for geom in f.geometry.geoms:
                print('looping through polygons in multipoly')
                inside = point_in_polygon(x, y, geom.exterior.coords)
        
        #print(type(f.geometry))
        if type(f) == MultiPolygon:
            print('HI')
            #print(type(f.geometry))
            #print(type(f.geometry.geoms[0]))
        #inside = point_in_polygon(x, y, f.geometry.exterior.coords)
        i = i + 1


    
    print('Done, took {}'.format(datetime.datetime.now() - start))
    #for f in f2:
    #    f.geometry'''


def point_in_polygon(x, y, polygon):
    n = len(polygon)
    inside = False
    p1x, p1y, p1z = polygon[0]

    for i in range(n+1):
        p2x, p2y, p2z = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside




#check()




'''polygon = [(0, 10), (10, 10), (10, 0), (0, 0)]

point_x = 11
point_y = 5

# Call the function with the points and the polygon
print(point_in_polygon(point_x, point_y, polygon))'''

def load_file():
    kml_file = kml.KML()
    kml_file.from_string(open('static/drone_nofly_dk.kml', encoding='utf-8').read())
    global features
    features = list(list(kml_file.features())[0].features())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5004,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    load_file()
    app.run(host=args.address, port=args.port, debug=True, threaded=True)
