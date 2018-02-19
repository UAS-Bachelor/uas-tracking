from flask import Flask, render_template, url_for
import sys
import argparse
from os import system

app = Flask(__name__)


@app.route('/map')
def index():
    return render_template('map.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5001,
                        help='specify which port to run this service on')
    args = parser.parse_args()
    args.prog = sys.argv[0].split('/')[-1].split('.')[0]

    print('Running {} service'.format(args.prog))
    system('title {} service on port {}'.format(args.prog, args.port))
    app.run(port=args.port, debug=True)
