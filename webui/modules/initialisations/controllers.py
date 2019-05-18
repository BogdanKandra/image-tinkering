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
import backend.utils as utils


init_mod = Blueprint('initialisations', __name__, url_prefix='/initialisations')

@init_mod.route('/', methods=['POST'])
def initialise():
    files = request.get_json()['files']
    images = files['image']
    videos = files['video']
    
    for image in images:
        # Initialise the data needed for each image
        filePath = os.path.join(app.config['IMAGES_DIR'], image)
        imageFile = cv2.imread(filePath, cv2.IMREAD_UNCHANGED)
        imageNameComponents = image.split('.')

        if utils.isGrayscale(imageFile):
            # Compute the padded image
            imageH, imageW = imageFile.shape[:2]
#            paddedH, paddedW = 2 * imageH, 2 * imageW
#            paddedImage = np.zeros((paddedH, paddedW), np.uint8)
#            paddedImage[0:imageH, 0:imageW] = imageFile
#            
#            # Compute the FFT of the padded image
#            paddedImageFFT = np.fft.fftshift(np.fft.fft2(paddedImage))
#            
#            # Serialise the FFT of the padded image
#            pickleName = imageNameComponents[0] + '_fft.pickle'
#            picklePath = os.path.join(app.config['TEMP_DATA'], pickleName)
#            file = open(picklePath, 'wb')
#            pickle.dump(paddedImageFFT, file)
#            file.close()
        else:
            # Compute the R, G, B channels of the image
            imageChannels = utils.getChannels(imageFile)
            
#            # Compute the padded image
#            imageH, imageW, channels = imageFile.shape
#            paddedH, paddedW = 2 * imageH, 2 * imageW
#            paddedImage = np.zeros((paddedH, paddedW, channels), np.uint8)
#            paddedImage[0:imageH, 0:imageW] = imageFile
#            
#            # Compute the R, G, B channels of the padded image
#            paddedImageChannels = utils.getChannels(paddedImage)
#            
#            # Compute the FFT of the padded image channels
#            paddedImageFFTs = [np.fft.fftshift(np.fft.fft2(channel)) for channel in paddedImageChannels]
            
            # Serialise the image channels
            i = 0
            for c in 'bgr':
                pickleName = imageNameComponents[0] + '_' + c + '.pickle'
                picklePath = os.path.join(app.config['TEMP_DATA'], pickleName)
                file = open(picklePath, 'wb')
                pickle.dump(imageChannels[i], file)
                file.close()
                i += 1
            
#            # Serialise the FFTs of the padded image channels
#            i = 0
#            for c in 'bgr':
#                pickleName = imageNameComponents[0] + '_' + c + '_fft.pickle'
#                picklePath = os.path.join(app.config['TEMP_DATA'], pickleName)
#                file = open(picklePath, 'wb')
#                pickle.dump(paddedImageFFTs[i], file)
#                file.close()
#                i += 1
    
    return make_response(jsonify('Initialisations finished!'), 200)
