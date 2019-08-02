"""
Created on Fri May 17 17:39:42 2019

@author: Bogdan
"""
import numpy as np


def flip(image, parameters):
    """Flips an image along the horizontal, vertical axis or both.
    
    Arguments:
        *image* (NumPy array) -- the image to flip
        
        *parameters* (dictionary) -- a dictionary containing following keys:
            
            *axis* (str, optional) -- the axis along which to flip the image;
            possible values are *horizontal*, *vertical* and *both*; default 
            value is *horizontal*
    
    Returns:
        NumPy array uint8 -- the flipped image
    """
    if 'axis' in parameters:
        axis = parameters['axis']
    else:
        axis = 'horizontal'
    
    resultImage = np.zeros(image.shape, dtype=np.uint8)
    if axis == 'vertical':
        for i in range(image.shape[0]):
            resultImage[i] = image[image.shape[0] - i - 1]
#        resultImage = np.flipud(image)
    elif axis == 'horizontal':
        for j in range(image.shape[1]):
            resultImage[:,j] = image[:,image.shape[1] - j - 1]
#        resultImage = np.fliplr(image)
    else:
        # Flip vertically
        resultTemp = np.zeros(image.shape, dtype=np.uint8)
        for i in range(image.shape[0]):
            resultTemp[i] = image[image.shape[0] - i - 1]

        # Flip horizontally
        for j in range(image.shape[1]):
            resultImage[:,j] = resultTemp[:,image.shape[1] - j - 1]
        
#        resultImage = np.fliplr(image)
#        resultImage = np.flipud(resultImage)
    
    return resultImage

def mirror(image, parameters):
    """Mirrors an image along the horizontal, vertical axis or both
    and pastes the result besides the original image, in the desired location.
    
    Arguments:
        *image* (NumPy array) -- the image to mirror
        
        *parameters* (dictionary) -- a dictionary containing following keys:
            
            *axis/location* (str, optional) -- the axis along which to flip the
            image; also, the location where the flipped image will be pasted.
            Possible values are *horizontal/left*, *horizontal/right*,
            *vertical/top*, *vertical/bottom*, *both/left/top*, *both/left/bottom*,
            *both/right/top*, *both/right/bottom*; default value is *horizontal/right*
    
    Returns:
        NumPy array uint8 -- the mirror image
    """
    if 'axis/location' in parameters:
        components = parameters['axis/location'].split('/')
        axis = components[0]
        if components[0] == 'both':
            locationH = components[1]
            locationV = components[2]
        else:
            location = components[1]
    else:
        axis = 'horizontal'
        location = 'right'
    
    # Use the flip function to flip the input image accordingly
    params = {'axis': axis}
    if axis != 'both':
        flipped = flip(image, params)
        
        # Create the mirror image according to the location parameter
        if location == 'left':
            mirror = np.hstack((flipped, image))
        elif location == 'right':
            mirror = np.hstack((image, flipped))
        elif location == 'top':
            mirror = np.vstack((flipped, image))
        else:
            mirror = np.vstack((image, flipped))
    else:
        flippedH = flip(image, {'axis': 'horizontal'})
        flippedV = flip(image, {'axis': 'vertical'})
        flippedBoth = flip(flippedV, {'axis': 'horizontal'})
        
        # Create the mirror image according to the location parameter
        if locationH == 'left':
            mirror1 = np.hstack((flippedH, image))
            mirror2 = np.hstack((flippedBoth, flippedV))
        else:
            mirror1 = np.hstack((image, flippedH))
            mirror2 = np.hstack((flippedV, flippedBoth))
        
        if locationV == 'top':
            mirror = np.vstack((mirror2, mirror1))
        else:
            mirror = np.vstack((mirror1, mirror2))
    
    return mirror
