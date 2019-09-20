"""
Created on Thu May 16 11:36:41 2019

@author: Bogdan
"""
import magic
import os, time
from flask import current_app as app
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from werkzeug import secure_filename
from werkzeug.exceptions import abort, RequestEntityTooLarge


upload_mod = Blueprint('uploads', __name__, url_prefix='/uploads')

@upload_mod.route('/inputs', methods=['POST'])
def upload_inputs():
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
        
        # Only save the file if it is an image or a video
        if mimeType.startswith('image/') or mimeType.startswith('video/'):
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

@upload_mod.route('/extrainputs', methods=['POST'])
def upload_extra_inputs():

    filesDict = request.files
    imageName = request.form['image-name']

    mime = magic.Magic(mime=True)
    savedFiles = {
            'image': [],
            'video': []
            }
    
    for key in filesDict:
        file = filesDict[key]
        mimeType = mime.from_buffer(file.stream.read(1024))
        file.stream.seek(0) # Move the file pointer back to the start of buffer
        
        # Only save the file if it is an image
        if mimeType.startswith('image/'):
            uploadsDir = app.config['EXTRA_IMAGES_DIR']
            filetype = 'image'
            
            name = imageName.split('.')[0][1:] + '_' + secure_filename(file.filename)
            uploadPath = os.path.join(uploadsDir, name)
            
            try:
                file.save(uploadPath)
                savedFiles[filetype].append(name)
            except RequestEntityTooLarge:
                errorMessage = 'File could not be uploaded. Maximum size must be 50 MB'
                abort(413, errorMessage)
    
    return make_response(jsonify(savedFiles), 200)
