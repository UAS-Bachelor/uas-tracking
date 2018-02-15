from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/map')
def index():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
