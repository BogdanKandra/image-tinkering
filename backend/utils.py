"""
Created on Sun Mar 10 15:12:37 2019

@author: Bogdan
"""
import copy
import cv2
from matplotlib import pyplot as plt
import numpy as np


def is_grayscale(image):
    """ Takes an image as parameter and decides whether the image
    is grayscale or not
    """
    return len(image.shape) == 2

def is_color(image):
    """ Takes an image as parameter and decides whether the image
    is color or not
    """
    return len(image.shape) != 2

def get_channels(image):
    """ Takes an image as parameter and returns a list containing
    its R, G, B (, A) channels or the image itself, if it is grayscale
    """
    return [copy.deepcopy(image)] if is_grayscale(image) else cv2.split(image)

def merge_channels(channels):
    """ Takes a list of channels as input and outputs the image obtained by
    merging the channels
    """
    return channels[0] if len(channels) == 1 else cv2.merge(tuple(channels))

def get_FFTs(image):
    """ Takes an image as parameter and returns a list containing
    the Fast Fourier Transforms of each of the image's channels
    """
    return [np.fft.fftshift(np.fft.fft2(channel)) for channel in get_channels(image)]

def fft_plot(image, cmap=None):
    """ Takes a frequency domain image and displays its spectrum

    Arguments:
        image (numPy array) -- the image to be displayed

        cmap (str) -- optional, the color map to be used

    Returns:
        Nothing
    """
    # Take the magnitudes and reduce values by logarithming
    magnitudes = np.log(np.abs(image) + 1)

    plt.figure()
    plt.imshow(magnitudes, cmap)
    plt.show()

def resize(image, new_width=80):
    """ Resizes an image while maintaining the aspect ratio

    Arguments:
        image (numPy array) -- the image to be resized

        new_width (int) -- optional, the new width (in pixels) of the resized image
    """
    h, w = image.shape[:2]
    aspect_ratio = h / w
    new_height = int(aspect_ratio * new_width)
    new_dim = (new_width, new_height)

    return cv2.resize(image, new_dim)
