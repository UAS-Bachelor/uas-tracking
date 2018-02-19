from flask import Flask, render_template, url_for
import sys
import argparse

app = Flask(__name__)


@app.route('/map')
def index():
    return render_template('map.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5001,
                        help='specify which port to run this service on')
    args = parser.parse_args()

    print('Running {} service'.format(sys.argv[0].split('.')[0]))
    app.run(port=args.port, debug=True)
