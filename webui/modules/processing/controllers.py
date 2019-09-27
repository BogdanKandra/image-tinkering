"""
Created on Thu May 16 12:29:17 2019

@author: Bogdan
"""
import importlib
import os
import cv2
from flask import current_app as app
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify


PROCESSING_MOD = Blueprint('processing', __name__, url_prefix='/process')

@PROCESSING_MOD.route('/', methods=['POST'])
def process():
    data = request.get_json()['data']
    results_names = []  # Will contain the names of the resulting files

    # Iterate over each file, processing it
    for file_name in data:

        # Read the file
        file_path = os.path.join(app.config['IMAGES_DIR'], file_name)
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        # Check for the type of the first operation, 
        # in order to decide how the operations will be applied
        operation_list = data[file_name]
        first_operation_type = operation_list[0]['type']
        file_name, extension = file_name.split('.')
        multiple_outputs = False # Helps in deciding how to store the results

        if first_operation_type in ('one-to-one', 'many-to-one'):
            # Only one-to-one operations will follow, so operation chaining is possible
            starting_index = 0 # Stores the starting index for chaining the operations

            if first_operation_type == 'many-to-one':
                # Load the extra inputs needed for calling the many-to-one operation
                extra_inputs = load_extra_inputs(file_name, operation_list[0]['extras'])

                # Make the operation call
                image = call_module_function(image, operation_list[0], extra_inputs)
                starting_index = 1

            # Iterate over each of the remaining operations ('one-to-one' or 'one-to-many'), applying them in order
            for i in range(starting_index, len(operation_list)):
                if operation_list[i]['type'] == 'one-to-many':
                    images = call_module_function(image, operation_list[i])
                    multiple_outputs = True
                else:
                    image = call_module_function(image, operation_list[i])
        elif first_operation_type in ('one-to-many', 'many-to-many'):
            # Do not expect any other operations to follow; this operation yields a list of results
            multiple_outputs = True
            
            if first_operation_type == 'one-to-many':
                # Make the operation call
                images = call_module_function(image, operation_list[0])
            else:
                # Load the extra inputs needed for calling the many-to-many operation
                extra_inputs = load_extra_inputs(file_name, operation_list[0]['extras'])

                # Make the operation call
                images = call_module_function(image, operation_list[0], extra_inputs)
        
        if multiple_outputs:
            # Save the results in temp zone
            i = 1
            for result in images:
                result_name = file_name + '_processed_' + str(i) + '.' + extension
                result_path = os.path.join(app.config['TEMP_DATA'], result_name)
                cv2.imwrite(result_path, result)
                results_names.append(result_name)
                i += 1
        else:
            # Save the result in temp zone, with name key + '_processed'
            result_name = file_name + '_processed.' + extension
            result_path = os.path.join(app.config['TEMP_DATA'], result_name)
            cv2.imwrite(result_path, image)
            results_names.append(result_name)

    # Return results_names
    return make_response(jsonify(results_names), 200)

def call_module_function(*arguments):
    """ Dynamically calls specified function from specified package and module,
    on the given image. If given two arguments, it will simply call the function
    on the image, with the given arguments; if given three arguments, it will
    call the function on the image, with the given arguments and the given
    list of extra inputs (for many-to operations)
    """
    # Unwind parameters and gather the operation details
    image, parameter_object = arguments[0], arguments[1]
    package, module, function = parameter_object['function'].split('.')
    parameters = parameter_object['params']

    # Call the requested function on the image
    imported_module = importlib.import_module('backend.' + package + '.' + module)
    if len(arguments) == 2:
        result = getattr(imported_module, function)(image, parameters)
    elif len(arguments) == 3:
        result = getattr(imported_module, function)(image, arguments[2], parameters)

    return result

def load_extra_inputs(file_name, extra_inputs_names):
    """ Loads the extra inputs needed for calling a 'many-to' operation """
    extra_inputs = {}

    for i in range(len(extra_inputs_names)):
        extra_file_name = file_name + '_' + extra_inputs_names[i]
        extra_file_extension = [file.split('.')[1] for file in os.listdir(app.config['EXTRA_IMAGES_DIR']) if file.startswith(extra_file_name)][0]
        extra_image_path = os.path.join(app.config['EXTRA_IMAGES_DIR'], extra_file_name + '.' + extra_file_extension)
        extra_image = cv2.imread(extra_image_path, cv2.IMREAD_UNCHANGED)
        
        extra_inputs[extra_inputs_names[i]] = extra_image

    return extra_inputs
