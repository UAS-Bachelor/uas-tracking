from flask import Flask, render_template, url_for, request, json
import requests
import sys
from configobj import ConfigObj
import argparse
import time
import os

app = Flask(__name__)

__services_config = os.path.realpath(__file__) + '/../../../services.ini'
configobj = ConfigObj(__services_config)


@app.route('/map2d')
def map():
    return render_template('map.html')


@app.route('/map2d/<id>/<start_time>/<end_time>')
def map_2d_with_params(id, start_time, end_time):
    try:
        cfg = configobj['drone_information']
        request.path = '/{}/{}/{}'.format(id, start_time, end_time)
        drone_route_list = json.loads(__get_url(cfg))
        #drone_route_list = spline_interpolate(drone_route_list, 2)
        route_duration = epoch_to_time(drone_route_list[-1]['time'] - drone_route_list[0]['time'])
    except requests.exceptions.ConnectionError:
        return 'Drone information service unavailable'
    return render_template('map.html', drone_route_list=drone_route_list, route_duration=route_duration)


def epoch_to_time(epoch):
    return time.strftime('%H:%M:%S', time.gmtime(epoch))


def __get_url(cfg):
    if(request.remote_addr == '127.0.0.1'):
        return requests.get('http://127.0.0.1:{}{}'.format(cfg['port'], request.path)).text
    else:
        return requests.get('http://{}:{}{}'.format(cfg['host'], cfg['port'], request.path)).text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1',
                        help='specify which host to run this service on')
    parser.add_argument('-p', '--port', type=int, default=5002,
                        help='specify which port to run this service on')
    parser.add_argument('-v', '--version', type=float, default=0,
                        help='specify which version of the service this is')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service version {}'.format(args.prog, args.version))
    os.system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=True, threaded=True)
