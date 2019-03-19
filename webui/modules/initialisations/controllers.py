"""
Created on Sun Mar 10 14:33:41 2019

@author: Bogdan
"""
import os, sys
import cv2
import numpy as np
import pickle
from flask import current_app as app
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template
# Import backend module
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(os.path.join(projectPath))
import backend.basic_operations as ops


init_mod = Blueprint('initialisations', __name__, url_prefix='/initialisations')

@init_mod.route('/', methods=['POST'])
def initialise():

    files = request.get_json()['files']
    print('>>>', app.config['IMAGES_DIR'])
    print('>>>', app.config['VIDEOS_DIR'])
    
    # TODO - Also initialise videos
#    for file in files: # Initialise the data needed for each file
#        print('File:', file)
#        filePath = os.path.join(projectPath, 'webui', 'static', 'uploads', 'images', file)
#        image = cv2.imread(filePath, cv2.IMREAD_UNCHANGED)
#
#        if ops.isGrayscale(image):
#            # Compute the padded image
#            imageH, imageW = image.shape[:2]
#            paddedH, paddedW = 2 * imageH, 2 * imageW
#            paddedImage = np.zeros((paddedH, paddedW), np.uint8)
#            paddedImage[0:imageH, 0:imageW] = image
#            
#            # Compute the FFT of the padded image
#            paddedImageFFT = np.fft.fftshift(np.fft.fft2(paddedImage))
#            
#            # Serialise the FFT of the padded image
            
    
    # Calculam R, G, B
    # Calculam paddedImage R, G, B
    # FFT pentru paddedImage R, G, B
    # Serializare fiecare

    return make_response(jsonify('Initialisations finished!'), 200)
