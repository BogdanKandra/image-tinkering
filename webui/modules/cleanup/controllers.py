"""
Created on Fri May 17 13:10:30 2019

@author: Bogdan
"""
import os
from flask import current_app as app
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify


cleanup_mod = Blueprint('cleanup', __name__, url_prefix='/cleanup')

@cleanup_mod.route('/', methods=['POST'])
def cleanup():
    filenames = request.get_json()['filenames']
    
    for filename in filenames:
        # Delete the processed file
        processed_path = os.path.join(app.config['TEMP_DATA'], filename)
        if os.path.exists(processed_path):
            os.remove(processed_path)
        
        # Delete the pickled channels
        unprocessed_filename = filename.rsplit('_', 1)[0]
        for c in 'rgba':
            pickle_name = unprocessed_filename + '_' + c + '.pickle'
            pickle_path = os.path.join(app.config['TEMP_DATA'], pickle_name)
            if os.path.exists(pickle_path):
                os.remove(pickle_path)
        
        # Delete the uploaded file
        extension = filename.split('.')[1]
        uploaded_name = unprocessed_filename + '.' + extension
        uploaded_path = os.path.join(app.config['IMAGES_DIR'], uploaded_name)
        if os.path.exists(uploaded_path):
            os.remove(uploaded_path)
    
    return make_response(jsonify('E ok'), 200)
