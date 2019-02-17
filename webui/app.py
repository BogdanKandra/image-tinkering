"""
Created on Wed Jan 23 21:20:15 2019

@author: Bogdan
"""
from flask.app import Flask
from flask.templating import render_template
from flask import request
from werkzeug import secure_filename
import sys, os

# Paths management
APP_ROOT = os.path.dirname(os.path.abspath(__name__))
IMAGES_UPLOAD_DIRECTORY = 'static\\uploads\\images'
VIDEO_UPLOAD_DIRECTORY = 'static\\uploads\\videos'

app = Flask(__name__)
#app.config['UPLOADED_FILES_DEST'] = UPLOAD_DIRECTORY
#app.config['UPLOAD_FOLDER'] = UPLOAD_DIRECTORY

# Binding routes
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
    filesDict = request.files

    for key in filesDict:
        file = filesDict[key]
        uploadPath = os.path.join(APP_ROOT, IMAGES_UPLOAD_DIRECTORY, secure_filename(file.filename))
        file.save(uploadPath)
    return 'HAHAHA'

@app.route('/redchannel', methods=['POST'])
def redchannel():
    """ The user makes a POST request, sending the name of the file(s) to be
    operated on. The proper function is applied, obtaining a new image, saving
    it in the temp zone, and sending the path of the image to the client
    """

# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
