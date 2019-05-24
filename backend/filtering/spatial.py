"""
Created on Sat May 18 16:58:05 2019

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

def sepia(image, parameters={}):
    """Applies a **Sepia Filter** on an image. \n
    
    Arguments:
        *image* (NumPy array) -- the image to be filtered
        
        *parameters* (dictionary) -- an empty parameter dictionary
        
    Returns:
        NumPy array uint8 -- the filtered image    
    """
    # Apply the Sepia formulas
    if utils.isColor(image):
        result_red = image[:,:,2] * 0.393 + image[:,:,1] * 0.769 + image[:,:,0] * 0.189
        result_green = image[:,:,2] * 0.349 + image[:,:,1] * 0.686 + image[:,:,0] * 0.168
        result_blue = image[:,:,2] * 0.272 + image[:,:,1] * 0.534 + image[:,:,0] * 0.131
    else:
        result_red = image * 0.393 + image * 0.769 + image * 0.189
        result_green = image * 0.349 + image * 0.686 + image * 0.168
        result_blue = image * 0.272 + image * 0.534 + image * 0.131
    
    # Trim values greater than 255
    result_red = np.where(result_red > 255, 255, result_red)
    result_green = np.where(result_green > 255, 255, result_green)
    result_blue = np.where(result_blue > 255, 255, result_blue)
    
    # Round the values and convert to int
    result_red = np.uint8(np.rint(result_red))
    result_green = np.uint8(np.rint(result_green))
    result_blue = np.uint8(np.rint(result_blue))
    
    sepia = cv2.merge((result_blue, result_green, result_red))
    
    return sepia

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