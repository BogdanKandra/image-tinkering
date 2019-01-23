"""
Created on Wed Jan 23 21:20:15 2019

@author: Bogdan
"""
from flask.app import Flask
from flask.templating import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def testing():
    return 'Alta pagina'

@app.route('/operation/<name>')
def operation(name):
    return render_template('test.html', numele=name)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
