"""
Created on Sat Aug  3 13:45:13 2019

@author: Bogdan
"""
import os
import sys
import numpy as np
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def pixels_shuffle(channels, state):
    """ Shuffles the pixels of an image """
    # Shuffle the pixels in each channel, with the same permutation
    for channel in channels:
        pixel_list = np.ravel(channel)  # Flattens the channel matrix to an array
        np.random.shuffle(pixel_list)
        channel = np.reshape(pixel_list, channel.shape)
        # Reset the state so that next shuffle is same permutation
        np.random.set_state(state)

    shuffled_image = utils.merge_channels(channels)

    return shuffled_image

def lines_shuffle(channels, state):
    """ Shuffles the lines of an image (The pixels on each line are left unchanged) """
    # Shuffle the lines in each channel, with the same permutation
    for channel in channels:
        np.random.shuffle(channel)
        # Reset the state so that next shuffle is same permutation
        np.random.set_state(state)

    shuffled_image = utils.merge_channels(channels)

    return shuffled_image

def columns_shuffle(channels, state):
    """ Shuffles the columns of an image (The pixels on each column are left unchanged) """
    # Shuffle the columns in each channel, with the same permutation
    for channel in channels:
        transpose = np.transpose(channel)
        np.random.shuffle(transpose)
        channel = np.transpose(transpose)
        # Reset the state so that next shuffle is same permutation
        np.random.set_state(state)

    shuffled_image = utils.merge_channels(channels)

    return shuffled_image

def channels_shuffle(channels):
    """ Shuffles the channels of an image """
    # Keep shuffling the indices list until a non-stationary permutation has
    # been obtained, as to ensure the output image is not the same as the input
    indices = np.arange(len(channels))
    while (np.arange(len(channels)) == indices).all() and len(channels) != 1:
        np.random.shuffle(indices)

    # Build the output image by merging the channels in the shuffled order
    shuffled_channels = []
    for i in indices:
        shuffled_channels.append(channels[i])

    shuffled_image = utils.merge_channels(shuffled_channels)

    return shuffled_image

def shuffle(image, extra_inputs, parameters):
    """ Shuffles elements from an image.

    Arguments:
        *image* (NumPy array) -- the image to be shuffled

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs
        for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *criterion* (str, optional) -- the criterion to shuffle the image
            by; possible values are *pixels*, *lines*, *columns* and *channels*;
            default value is *channels*

    Returns:
        list of NumPy array uint8 -- list containing the shuffled image
    """
    state = np.random.get_state()
    channels = utils.get_channels(image)

    if 'criterion' in parameters:
        if parameters['criterion'] == 'pixels':
            shuffled_image = pixels_shuffle(channels, state)
        elif parameters['criterion'] == 'lines':
            shuffled_image = lines_shuffle(channels, state)
        elif parameters['criterion'] == 'columns':
            shuffled_image = columns_shuffle(channels, state)
        else:
            shuffled_image = channels_shuffle(channels)
    else:
        shuffled_image = channels_shuffle(channels)

    return [shuffled_image]
