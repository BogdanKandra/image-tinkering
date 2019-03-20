"""
Created on Wed Jan 23 21:20:15 2019

@author: Bogdan
"""
import sys, os, time
import magic

from flask import Flask, request
from flask.helpers import make_response, send_from_directory
from flask.json import jsonify
from flask.templating import render_template
from werkzeug import secure_filename
from werkzeug.exceptions import abort, RequestEntityTooLarge
from modules.test.controllers import test_mod
from modules.initialisations.controllers import init_mod


# Paths management
APP_ROOT = os.path.dirname(os.path.abspath(__name__))
IMAGES_UPLOAD_DIRECTORY = os.path.join('static', 'uploads', 'images')
VIDEOS_UPLOAD_DIRECTORY = os.path.join('static', 'uploads', 'videos')
TEMP_DATA_DIRECTORY = os.path.join('static', 'tempdata')

# Application instantiation and configuration
app = Flask(__name__)
app.config['IMAGES_DIR'] = os.path.join(APP_ROOT, IMAGES_UPLOAD_DIRECTORY)
app.config['VIDEOS_DIR'] = os.path.join(APP_ROOT, VIDEOS_UPLOAD_DIRECTORY)
app.config['TEMP_DATA'] = os.path.join(APP_ROOT, TEMP_DATA_DIRECTORY)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Blueprints Registration
app.register_blueprint(test_mod)
app.register_blueprint(init_mod)

# Error handling
@app.errorhandler(413)
def file_too_large(err):
    return make_response(jsonify('File too big'), 413)

# Binding routes
@app.route('/')
def index():
    return make_response(render_template('index.html'), 200)

@app.route('/uploads', methods=['POST'])
def uploads():
#    print(request, file=sys.stdout)
    filesDict = request.files
    mime = magic.Magic(mime=True)
    savedFiles = {
            'image': [],
            'video': []
            }

    for key in filesDict:
        file = filesDict[key]
        mimeType = mime.from_buffer(file.stream.read(1024))
        file.stream.seek(0) # Move the file pointer back to the start of buffer

        if mimeType.startswith('image/') or mimeType.startswith('video/'):
            # Only save the file if it is an image or a video
            if mimeType.startswith('image/'):
                uploadsDir = app.config['IMAGES_DIR']
                filetype = 'image'
            else:
                uploadsDir = app.config['VIDEOS_DIR']
                filetype = 'video'
                
            # Append the timestamp to the filename
            timestamp = str(time.time())
            if '.' in timestamp: # Also append the fractional part if available
                timestamp = "".join(timestamp.split('.'))
            
            name = secure_filename(file.filename)
            nameComponents = name.split('.')
            name = nameComponents[0] + '_' + timestamp + '.' + nameComponents[1]
                
            uploadPath = os.path.join(uploadsDir, name)
            try:
                file.save(uploadPath)
                savedFiles[filetype].append(name)
            except RequestEntityTooLarge:
                errorMessage = 'File could not be uploaded. Maximum size must be 50 MB'
                abort(413, errorMessage)
                
    return make_response(jsonify(savedFiles), 200)

@app.route('/redchannel', methods=['POST'])
def redchannel():
    """ The user makes a POST request, sending the name of the file(s) to be
    operated on. The proper function is applied, obtaining a new image, saving
    it in the temp zone, and sending the path of the image to the client
    """

# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
