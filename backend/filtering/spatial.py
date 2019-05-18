"""
Created on Sat May 18 16:58:05 2019

@author: Bogdan
"""
import os, sys
import numpy as np
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(projectPath)
from backend import utils


def grayscale(image, parameters={}):
    """Applies a **Grayscale Filter** on an image. \n
    
    Arguments:
        *image* (NumPy array) -- the image to be filtered
        
        *parameters* (dictionary) -- an empty parameter dictionary
    
    Returns:
        NumPy array uint8 -- the filtered image
    """
    if utils.isGrayscale(image):
        gray_image = image
    else:
        gray_image = image[:,:,0] * 0.11 + image[:,:,1] * 0.59 + image[:,:,2] * 0.3
        gray_image = np.uint8(np.rint(gray_image))
    
    return gray_image

def negative(image, parameters={}):
    """Applies a **Negative Filter** on an image. \n
    
    Arguments:
        *image* (NumPy array) -- the image to be filtered
        
        *parameters* (dictionary) -- an empty parameter dictionary
        
    Returns:
        NumPy array uint8 -- the filtered image
    """
    negative_image = 255 - image
    
    return negative_image