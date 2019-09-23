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


CLEANUP_MOD = Blueprint('cleanup', __name__, url_prefix='/cleanup')

@CLEANUP_MOD.route('/tempdata', methods=['POST'])
def cleanup_tempdata():
    ''' Deletes the resulting images (processed images and pickles)
    for each of the given list of processed files '''
    filenames = request.get_json()['filenames']

    for filename in filenames:
        # Delete the processed file
        processed_path = os.path.join(app.config['TEMP_DATA'], filename)
        try:
            if os.path.exists(processed_path):
                os.remove(processed_path)
            else:
                print('>>> [/cleanup/tempdata] Requested file does not exist:', filename)
        except OSError as err:
            print('>>> [/cleanup/tempdata] Error deleting file:', filename)
            print('>>>', err)

        # Delete the pickled channels
        unprocessed_filename = filename.rsplit('_', 1)[0]
        for channel in 'rgba':
            pickle_name = unprocessed_filename + '_' + channel + '.pickle'
            pickle_path = os.path.join(app.config['TEMP_DATA'], pickle_name)
            try:
                if os.path.exists(pickle_path):
                    os.remove(pickle_path)
                else:
                    print('>>> [/cleanup/tempdata] Pickle does not exist:', pickle_name)
            except OSError as err:
                print('>>> [/cleanup/tempdata] Error deleting pickle:', pickle_name)
                print('>>>', err)

    return make_response(jsonify('Server: Result files have been deleted'), 200)

@CLEANUP_MOD.route('/pickles', methods=['POST'])
def cleanup_pickles():
    ''' Deletes the pickle files which resulted after the initialisation process,
    for each of the given keys in the data to process or list of filenames to process '''
    filenames = request.get_json()['filenames']

    for filename in filenames:
        # Delete the pickled channels
        unprocessed_filename = filename.rsplit('.')[0]
        for channel in 'rgba':
            pickle_name = unprocessed_filename + '_' + channel + '.pickle'
            pickle_path = os.path.join(app.config['TEMP_DATA'], pickle_name)
            try:
                if os.path.exists(pickle_path):
                    os.remove(pickle_path)
                else:
                    print('>>> [/cleanup/pickles] Pickle does not exist:', pickle_name)
            except OSError as err:
                print('>>> [/cleanup/pickles] Error deleting pickle:', pickle_name)
                print('>>>', err)

    return make_response(jsonify('Server: Pickle files have been deleted'), 200)

@CLEANUP_MOD.route('/uploads', methods=['POST'])
def cleanup_uploads():
    ''' Deletes uploaded images (input image and extra input images, if any),
    for each of the given keys in the data to process or list of filenames to process '''
    data = request.get_json()['data']

    for file_name in data:
        # Delete the file from uploads/images
        file_path = os.path.join(app.config['IMAGES_DIR'], file_name)

        try:
            os.remove(file_path)
        except OSError as err:
            print('>>> [/cleanup/uploads] Error deleting file:', file_name)
            print('>>>', err)

        # Delete associated extra inputs from uploads/images/extra_inputs
        extra_inputs = [file for file in os.listdir(app.config['EXTRA_IMAGES_DIR'])
                        if file.startswith(file_name.split('.')[0] + '_')]

        for extra in extra_inputs:
            extra_path = os.path.join(app.config['EXTRA_IMAGES_DIR'], extra)

            try:
                os.remove(extra_path)
            except OSError as err:
                print('>>> [/cleanup/uploads] Error deleting file:', extra)
                print('>>>', err)

    return make_response(jsonify('Server: Uploaded files have been deleted'), 200)

@CLEANUP_MOD.route('/extras', methods=['POST'])
def cleanup_extras():
    ''' Deletes extra input images associated to a particular input image '''
    image_name = request.get_json()['name']
    extra_inputs = [file for file in os.listdir(app.config['EXTRA_IMAGES_DIR'])
                    if file.startswith(image_name.split('.')[0] + '_')]

    for extra in extra_inputs:
        extra_path = os.path.join(app.config['EXTRA_IMAGES_DIR'], extra)

        try:
            os.remove(extra_path)
        except OSError as err:
            print('>>> [/cleanup/extras] Error deleting file:', extra)
            print('>>>', err)

    return make_response(jsonify('Server: Extra images have been deleted'), 200)
