"""
Created on Wed Jan 23 21:20:15 2019

@author: Bogdan
"""
from flask import Flask
from flask.templating import render_template
from flask import abort, jsonify, make_response, request
from werkzeug import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import sys, os
import magic

# Paths management
APP_ROOT = os.path.dirname(os.path.abspath(__name__))
IMAGES_UPLOAD_DIRECTORY = 'static\\uploads\\images'
VIDEOS_UPLOAD_DIRECTORY = 'static\\uploads\\videos'

# Application instantiation and configuration
app = Flask(__name__)
app.config['IMAGES_DEST'] = IMAGES_UPLOAD_DIRECTORY
app.config['VIDEOS_DEST'] = VIDEOS_UPLOAD_DIRECTORY
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024


# Binding routes
@app.route('/')
def index():
    return make_response(render_template('index.html'), 200)

@app.route('/test')
def testing():
    return make_response(jsonify('Alta pagina'), 200)

@app.route('/operation/<name>')
def operation(name):
    return make_response(render_template('test.html', numele=name), 200)

@app.route('/uploads', methods=['POST'])
def uploads():
#    print(request, file=sys.stdout)
    filesDict = request.files
    mime = magic.Magic(mime=True)

    for key in filesDict:
        file = filesDict[key]
        mimeType = mime.from_buffer(file.stream.read(1024))
        file.stream.seek(0) # Move the file pointer back to the start of buffer

        if mimeType.startswith('image/') or mimeType.startswith('video/'):
            # Only save the file if it is an image or a video
            if mimeType.startswith('image/'):
                uploadsDir = IMAGES_UPLOAD_DIRECTORY
            else:
                uploadsDir = VIDEOS_UPLOAD_DIRECTORY
                
            uploadPath = os.path.join(APP_ROOT, uploadsDir, secure_filename(file.filename))
            try:
                file.save(uploadPath)
            except RequestEntityTooLarge:
                errorMessage = 'File could not be uploaded. Maximum size must be 50 MB'
                abort(413, errorMessage)
    return make_response(jsonify('Files were uploaded successfully'), 200)

@app.route('/redchannel', methods=['POST'])
def redchannel():
    """ The user makes a POST request, sending the name of the file(s) to be
    operated on. The proper function is applied, obtaining a new image, saving
    it in the temp zone, and sending the path of the image to the client
    """

@app.errorhandler(413)
def file_too_large(err):
    return make_response(jsonify('File too big'), 413)

# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
