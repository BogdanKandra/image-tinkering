"""
Created on Fri Aug  9 15:26:45 2019

@author: Bogdan
"""
import os, sys
import cv2
import numpy as np
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(projectPath)
from backend import utils


def splitChannels(image, parameters):
    """ Splits an image into its channels and returns them.
    
    Arguments:
        *image* (NumPy array) -- the image to be split
        
        *parameters* (dictionary) -- a dictionary containing following keys:
            
            *spectrum* (str, optional) -- the spectrum in which the channels will
            be represented; possible values are *grayscale* and *color*; default
            value is *color*
    
    Returns:
        list of NumPy array uint8 -- the channels of the image
    """
    if utils.isColor(image):
        b = image[:,:,0]
        g = image[:,:,1]
        r = image[:,:,2]
        
        if 'spectrum' in parameters:
            spectrum = parameters['spectrum']
        else:
            spectrum = 'color'
        
        if spectrum == 'color':
            zeros = np.zeros((image.shape[:2]), dtype='uint8')
            b = cv2.merge([b, zeros, zeros])
            g = cv2.merge([zeros, g, zeros])
            r = cv2.merge([zeros, zeros, r])
        
        return [b, g, r]
    else:
        return [image]

def removeChannel(image, parameters):
    """
    """
    pass
