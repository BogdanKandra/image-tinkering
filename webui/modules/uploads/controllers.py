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

@upload_mod.route('/', methods=['POST'])
def upload():
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

@upload_mod.route('/purge', methods=['POST'])
def purge_uploads():
    data = request.get_json()['data']
    
    for file_name in data:
        # Attempt to delete the file from uploads/images
        file_path = os.path.join(app.config['IMAGES_DIR'], file_name)
        
        try:
            os.remove(file_path)
        except OSError as err:
            print('>>> [/uploads/purge/] Error deleting file:', file_path)
            print('>>>', err)
        
        # Attempt to delete associated extra inputs from uploads/images/extra_inputs
        extra_inputs = [file for file in os.listdir(app.config['EXTRA_IMAGES_DIR']) 
                            if file.startswith(file_name.split('.')[0] + '_')]
        
        for extra in extra_inputs:
            extra_path = os.path.join(app.config['EXTRA_IMAGES_DIR'], extra)
            
            try:
                os.remove(extra_path)
            except OSError as err:
                print('>>> [/uploads/purge/] Error deleting file:', extra_path)
                print('>>>', err)
    
    return make_response(jsonify('Files have been deleted'), 200)
