from flask import Flask, render_template, url_for, request
import requests
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map')
def map():
    try:
        map = requests.get('http://127.0.0.1:5001/map').content
    except requests.exceptions.ConnectionError:
        return 'Map service unavailable'
    return map

#Skal stå sammen med GET og POST - driller
#@app.route('/login', methods=['GET', 'POST'])
#def login():
#   if request.method == 'POST':
#        username = request.form['username']
#        password_candidate = request.form['password']
#        app.logger.info(username)
#        app.logger.info(password_candidate)
#
#    else: 
#        return render_template('http://127.0.0.1:5002/login')
        


if __name__ == '__main__':
    print('Running {} service'.format(os.path.basename(__file__).split('.')[0]))
    app.run(port=5000, debug=True)
