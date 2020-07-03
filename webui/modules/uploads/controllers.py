"""
Created on Thu May 16 11:36:41 2019

@author: Bogdan
"""
import os
import time
import magic
from flask import current_app as app
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort, RequestEntityTooLarge


UPLOAD_MOD = Blueprint('uploads', __name__, url_prefix='/uploads')

@UPLOAD_MOD.route('/inputs', methods=['POST'])
def upload_inputs():
    ''' Uploads the specified images and/or videos '''
    files = request.files
    mime = magic.Magic(mime=True)
    saved_files = {
        'image': [],
        'video': []
        }

    for key in files:
        file = files[key]
        mime_type = mime.from_buffer(file.stream.read(1024))
        file.stream.seek(0) # Move the file pointer back to the start of buffer

        # Only save the file if it is an image or a video
        if mime_type.startswith('image/') or mime_type.startswith('video/'):
            if mime_type.startswith('image/'):
                uploads_dir = app.config['IMAGES_DIR']
                filetype = 'image'
            else:
                uploads_dir = app.config['VIDEOS_DIR']
                filetype = 'video'

            # Append the timestamp to the filename
            timestamp = str(time.time())
            if '.' in timestamp: # Also append the fractional part if available
                timestamp = "".join(timestamp.split('.'))

            name = secure_filename(file.filename)
            name_components = name.split('.')
            name = name_components[0] + '_' + timestamp + '.' + name_components[1]

            upload_path = os.path.join(uploads_dir, name)
            try:
                file.save(upload_path)
                saved_files[filetype].append(name)
            except RequestEntityTooLarge:
                error_message = 'File could not be uploaded. Maximum size must be 50 MB'
                abort(413, error_message)

    return make_response(jsonify(saved_files), 200)

@UPLOAD_MOD.route('/extrainputs', methods=['POST'])
def upload_extra_inputs():
    ''' Uploads the specified extra input files, associated to the specified image '''
    files = request.files
    image_name = request.form['image-name']
    params_names = request.form['params-names'].split(',') # Convert string to list

    mime = magic.Magic(mime=True)
    saved_files = {
        'image': [],
        'video': []
        }

    i = 0
    for key in files:
        file = files[key]
        param_name = params_names[i]

        mime_type = mime.from_buffer(file.stream.read(1024))
        file.stream.seek(0) # Move the file pointer back to the start of buffer

        # Only save the file if it is an image
        if mime_type.startswith('image/'):
            uploads_dir = app.config['EXTRA_IMAGES_DIR']
            filetype = 'image'

            name = image_name.split('.')[0] + '_' + param_name + '.' + file.filename.split('.')[1]
            upload_path = os.path.join(uploads_dir, name)

            try:
                file.save(upload_path)
                saved_files[filetype].append(name)
            except RequestEntityTooLarge:
                error_message = 'File could not be uploaded. Maximum size must be 50 MB'
                abort(413, error_message)

        i += 1

    return make_response(jsonify(saved_files), 200)
