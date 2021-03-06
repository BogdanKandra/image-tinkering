"""
Created on Fri Aug  9 15:26:45 2019

@author: Bogdan
"""
import copy
import os
import sys
import cv2
import numpy as np
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def split_channels(image, extra_inputs, parameters):
    ''' Splits an image into its channels and returns them.

    Arguments:
        *image* (NumPy array) -- the image to be split

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *spectrum* (str, optional) -- the spectrum in which the channels will
            be represented; possible values are *grayscale* and *color*; default
            value is *color*

    Returns:
        list of NumPy array uint8 -- list containing the channels of the image
    '''
    if utils.is_color(image):
        b = image[:, :, 0]
        g = image[:, :, 1]
        r = image[:, :, 2]

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

    return [image]

def remove_channels(image, extra_inputs, parameters):
    ''' Zeroes out channels from an image.

    Arguments:
        *image* (NumPy array) -- the image from which to remove channels

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *channel(s)* (str) -- the channel(s) to be removed from the image;
            possible values are *red*, *green*, *blue*, *red & green*, *red &
            blue*, *green & blue*
    Returns:
        list of NumPy array uint8 -- list containing the image having the requested channels removed
    '''
    channels_information = parameters['channel(s)']
    image_copy = copy.deepcopy(image)

    if utils.is_color(image):
        if '&' in channels_information:
            # Zero out the two specified channels
            channels = channels_information.split(' & ')
            if channels[0] == 'red':
                image_copy[:, :, 2] = 0
            elif channels[0] == 'green':
                image_copy[:, :, 1] = 0

            if channels[1] == 'green':
                image_copy[:, :, 1] = 0
            elif channels[1] == 'blue':
                image_copy[:, :, 0] = 0
        else:
            # Zero out the specified channel
            if channels_information == 'red':
                image_copy[:, :, 2] = 0
            elif channels_information == 'green':
                image_copy[:, :, 1] = 0
            else:
                image_copy[:, :, 0] = 0

    return [image_copy]
