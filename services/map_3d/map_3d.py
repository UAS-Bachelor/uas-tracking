from flask import Flask, render_template, url_for
from flask_cors import CORS
import sys
import argparse
from os import system

app = Flask(__name__)
CORS(app)


@app.route('/map')
def index():
    return render_template('map.html')


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
    system('title {} service version {} on {}:{}'.format(
        args.prog, args.version, args.address, args.port))
    app.run(host=args.address, port=args.port, debug=False)