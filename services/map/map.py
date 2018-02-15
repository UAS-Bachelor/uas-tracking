from flask import Flask, render_template, url_for
import os

app = Flask(__name__)


@app.route('/map')
def index():
    return render_template('map.html')


if __name__ == '__main__':
    print('Running {} service'.format(os.path.basename(__file__).split('.')[0]))
    app.run(port=5001, debug=True)
