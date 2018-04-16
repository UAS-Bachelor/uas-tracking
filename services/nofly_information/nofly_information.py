from flask import Flask, request, jsonify, Response, send_from_directory, url_for, redirect
from flask_cors import CORS
import requests
import json
import argparse
import sys
import os


app = Flask(__name__)
CORS(app)


@app.route('/zones')
def get_nofly_zones_list():
    return redirect(url_for('static', filename='drone_nofly_dk.kml', _external=True))

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
    app.run(host=args.address, port=args.port, debug=True, threaded=True)