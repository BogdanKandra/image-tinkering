"""
Created on Sat Aug  3 13:45:13 2019

@author: Bogdan
"""
import os, sys
import numpy as np
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(projectPath)
from backend import utils


def shuffle(image, parameters):
    """ Shuffles elements from an image.
    
    Arguments:
        *image* (NumPy array) -- the image to be shuffled
        
        *parameters* (dictionary) -- a dictionary containing following keys:
            
            *criterion* (str, optional) -- the criterion to shuffle the image by;
            possible values are *pixels*, *lines* and *channels*; default value
            is *lines*
    """
    if 'criterion' in parameters:
        if parameters['criterion'] == 'pixels':
            return pixel_shuffle(image)
        elif parameters['criterion'] == 'lines':
            return lines_shuffle(image)
        elif parameters['criterion'] == 'channels':
            return channels_shuffle(image)
    else:
        return lines_shuffle(image)

def pixel_shuffle(image):
    """ Shuffles the pixels of an image. """
    state = np.random.get_state()
    channels = utils.getChannels(image)

    # Shuffle the pixels in each channel
    for channel in channels:
        pixel_list = np.ravel(channel) # Flattens the channel matrix to an array
        np.random.shuffle(pixel_list)
        channel = np.reshape(pixel_list, channel.shape)
        np.random.set_state(state) # Reset the state so that next shuffle is same permutation

    shuffled_image = utils.mergeChannels(channels)
    
    return shuffled_image

def lines_shuffle(image):
    """ Shuffles the lines of an image (The pixels on each line are left
    unchanged).
    """
    state = np.random.get_state()
    channels = utils.getChannels(image)

    # Shuffle the lines in each channel
    for channel in channels:
        np.random.shuffle(channel)
        np.random.set_state(state) # Reset the state so that next shuffle is same permutation

    shuffled_image = utils.mergeChannels(channels)
    
    return shuffled_image

def channels_shuffle(image):
    """ Shuffles the channels of an image. """
    channels = utils.getChannels(image)

    # Keep shuffling the indices list until a non-stationary permutation has been
    # obtained, as to ensure the output image is not the same as the input
    indices = np.arange(len(channels))
    while (np.arange(len(channels)) == indices).all() and len(channels) != 1:
        np.random.shuffle(indices)
    
    # Build the output image by merging the channels in the shuffled order
    shuffled_channels = []
    for i in indices:
        shuffled_channels.append(channels[i])
    
    shuffled_image = utils.mergeChannels(shuffled_channels)
    
    return shuffled_image

def columns_shuffle():
    pass


