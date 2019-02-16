"""
Created on Wed Jan 23 21:20:15 2019

@author: Bogdan
"""
from flask.app import Flask
from flask.templating import render_template
from flask import request
from werkzeug import secure_filename
import sys

UPLOAD_FOLDER = '/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def testing():
    return 'Alta pagina'

@app.route('/operation/<name>')
def operation(name):
    return render_template('test.html', numele=name)

@app.route('/uploads', methods=['POST'])
def uploads():
#    print(request, file=sys.stdout)
#    print('This is standard output', file=sys.stdout)
    files = request.files
    print(files, file=sys.stdout)
    for file in files:
        file.save(secure_filename(file.filename))
    return 'HAHAHA'

@app.route('/redchannel', methods=['POST'])
def redchannel():
    """ The user makes a POST request, sending the name of the file(s) to be
    operated on. The proper function is applied, obtaining a new image, saving
    it in the temp zone, and sending the path of the image to the client
    """

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
