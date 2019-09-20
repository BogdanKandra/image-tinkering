"""
Created on Sun Mar 10 14:33:41 2019

@author: Bogdan
"""
import os
import pickle
import sys
import cv2
import numpy as np
from flask import current_app as app
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template
# Import backend module
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(os.path.join(project_path))
import backend.utils as utils


INIT_MOD = Blueprint('initialisations', __name__, url_prefix='/initialisations')

@INIT_MOD.route('/', methods=['POST'])
def initialise():
    files = request.get_json()['files']
    images = files['image']
    videos = files['video']

    for image in images:
        # Initialise the data needed for each image
        file_path = os.path.join(app.config['IMAGES_DIR'], image)
        image_file = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        image_name_components = image.split('.')

        if utils.isGrayscale(image_file):
            # Compute the padded image
            image_h, image_w = image_file.shape[:2]
#            padded_h, padded_w = 2 * image_h, 2 * image_w
#            padded_image = np.zeros((padded_h, padded_w), np.uint8)
#            padded_image[0:image_h, 0:image_w] = image_file

#            # Compute the FFT of the padded image
#            padded_image_FFT = np.fft.fftshift(np.fft.fft2(padded_image))

#            # Serialise the FFT of the padded image
#            pickle_name = image_name_components[0] + '_fft.pickle'
#            pickle_path = os.path.join(app.config['TEMP_DATA'], pickle_name)
#            file = open(pickle_path, 'wb')
#            pickle.dump(padded_image_FFT, file)
#            file.close()
        else:
            # Compute the R, G, B channels of the image
            image_channels = utils.getChannels(image_file)

#            # Compute the padded image
#            image_h, image_w, channels = image_file.shape
#            padded_h, padded_w = 2 * image_h, 2 * image_w
#            padded_image = np.zeros((padded_h, padded_w, channels), np.uint8)
#            padded_image[0:image_h, 0:image_w] = image_file

#            # Compute the R, G, B channels of the padded image
#            padded_image_channels = utils.getChannels(padded_image)

#            # Compute the FFT of the padded image channels
#            padded_image_FFTs = [np.fft.fftshift(np.fft.fft2(channel)) for channel in padded_image_channels]

            # Serialise the image channels
            i = 0
            for c in 'bgr':
                pickle_name = image_name_components[0] + '_' + c + '.pickle'
                pickle_path = os.path.join(app.config['TEMP_DATA'], pickle_name)
                file = open(pickle_path, 'wb')
                pickle.dump(image_channels[i], file)
                file.close()
                i += 1

#            # Serialise the FFTs of the padded image channels
#            i = 0
#            for c in 'bgr':
#                pickle_name = image_name_components[0] + '_' + c + '_fft.pickle'
#                pickle_path = os.path.join(app.config['TEMP_DATA'], pickle_name)
#                file = open(pickle_path, 'wb')
#                pickle.dump(padded_image_FFTs[i], file)
#                file.close()
#                i += 1

    return make_response(jsonify('Server: Initialisations process completed successfully'), 200)
