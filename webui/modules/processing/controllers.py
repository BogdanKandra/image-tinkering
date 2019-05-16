"""
Created on Thu May 16 12:29:17 2019

@author: Bogdan
"""
import importlib, os
import cv2
from flask import current_app as app
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify


processing_mod = Blueprint('processing', __name__, url_prefix='/process')

@processing_mod.route('/', methods=['POST'])
def process():
    
    data = request.get_json()['data']
    results_names = []  # Will contain the names of the resulting files

    # Iterate over each file, processing it
    for file_name in data:
        
        # Read the file
        file_path = os.path.join(app.config['IMAGES_DIR'], file_name)
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        # Iterate over each operation, applying them in order
        operation_list = data[file_name]
        for operation in operation_list:
            
            package, module, function = operation['function'].split('.')
            parameters = operation['params']
            imported_module = importlib.import_module('backend.' + package + '.' + module)
            image = getattr(imported_module, function)(image, parameters)
            
        # Save the result in temp zone, with name key + '_processed'
        file_name, extension = file_name.split('.')
        result_name = file_name + '_processed.' + extension
        result_path = os.path.join(app.config['TEMP_DATA'], result_name)
        cv2.imwrite(result_path, image)
        
        # Append the resulting file name to results_names
        results_names.append(result_name)
    
    # Return results_names
    return make_response(jsonify(results_names), 200)
