from flask import Flask, render_template, url_for, request, redirect, jsonify
import json
import requests
import sys
import argparse
import os

app = Flask(__name__)
app.url_map.strict_slashes = False

__services_config_file = os.path.join(os.path.dirname(__file__), '../../cfg/services.json')
config = json.load(open(__services_config_file))


@app.route('/')
def index():
    return redirect('/routes')
    #return render_template('index.html')


@app.route('/routes', methods = ['GET', 'POST', 'DELETE'])
def routes():
    try:
        if request.method == 'GET':
            return get_drone_routes_list('drone_information')

        elif request.method == 'POST':
            return post_drone_route('drone_information')

        elif request.method == 'DELETE':
            return delete_drone_route('drone_information')
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable', 503


def get_drone_routes_list(service_name):
    drone_routes_list = json.loads(get(service_name))
    return render_template('route_list.html', drones=drone_routes_list)


def post_drone_route(service_name):
    return post(service_name)


def delete_drone_route(service_name):
    return delete(service_name)


@app.route('/routes/<routeid>')
def get_route_by_id(routeid):
    return render_template('route.html', routeid=routeid)


@app.route('/routes/<routeid>/2d')
def get_2d_map_by_routeid(routeid):
    try:
        map_2d = get('map_2d')
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return '2D Map service unavailable', 503
    return render_template('layout.html', html=map_2d)


@app.route('/routes/<routeid>/3d')
def get_3d_map_by_routeid(routeid):
    try:
        map_3d = get('map_3d')
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return '3D Map service unavailable', 503
    return render_template('layout.html', html=map_3d)


@app.route('/live')
def get_live():
    return render_template('live.html')


@app.route('/live/2d')
def get_2d_live_map():
    try:
        map_2d = get('map_2d')
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return '2D Map service unavailable', 503
    return render_template('layout.html', html=map_2d)


@app.route('/live/3d')
def get_3d_live_map():
    try:
        map_3d = get('map_3d')
    except requests.exceptions.HTTPError as exception:
        return jsonify(json.loads(exception.text)), exception.errno
    except requests.exceptions.ConnectionError:
        return '3D Map service unavailable', 503
    return render_template('layout.html', html=map_3d)


def get(service_name, path=''):
    url = get_url_string(service_name, path)
    response = requests.get(url)
    raise_for_status_code(response)
    return response.text


def post(service_name, path=''):
    url = get_url_string(service_name, path)
    response = requests.post(url, json=request.json)
    raise_for_status_code(response)
    return response.text


def delete(service_name, path=''):
    url = get_url_string(service_name, path)
    response = requests.delete(url, json=request.json)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='0.0.0.0',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5000,
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
