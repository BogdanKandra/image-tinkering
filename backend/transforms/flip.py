"""
Created on Fri May 17 17:39:42 2019

@author: Bogdan
"""
import numpy as np


def flip(image, parameters):
    """Flips an image along the horizontal or vertical axis.
    
    Arguments:
        *image* (NumPy array) -- the image to flip
        
        *parameters* (dictionary) -- a dictionary containing following keys:
            
            *axis* (str, optional) -- the axis along which to flip the image;
            possible values are *horizontal* and *vertical*; default value is 
            *horizontal*
    
    Returns:
        NumPy array uint8 -- the flipped image
    """
    
    if 'axis' in parameters:
        axis = parameters['axis']
    else:
        axis = 'horizontal'
    
    resultImage = np.zeros(image.shape, dtype=np.uint8)
    if axis == 'horizontal':
        for i in range(image.shape[0]):
            resultImage[i] = image[image.shape[0] - i - 1]
        #resultImage = np.flipud(image)
    else:
        for j in range(image.shape[1]):
            resultImage[:,j] = image[:,image.shape[1] - j - 1]
        #resultImage = np.fliplr(image)
    
    return resultImage
