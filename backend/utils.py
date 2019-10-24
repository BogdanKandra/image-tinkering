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

    plt.subplot(121)
    plt.imshow(image, cmap)
    plt.subplot(122)
    plt.imshow(magnitudes, cmap)

    plt.show()

def resize_dimension(image, new_height=0, new_width=0):
    ''' If one of the dimensions is not given, resizes an image to the specified height (or width),
    while maintaining the original aspect ratio. If given both dimensions, resizes an image to the
    fixed, specified dimensions

    Arguments:
        image (numPy array) -- the image to be resized

        new_height (int, optional) -- the new height (in pixels) of the resized image; the default
        value is 0, meaning that the image will not be resized by height

        new_width (int, optional) -- same as "new_height", except for the width. If both these
        arguments are left as default, the original image will be returned
    '''
    image_h, image_w = image.shape[:2]
    aspect_ratio = image_w / image_h

    if new_height < 0 or new_width < 0:
        raise ValueError('"new_height" and "new_width" must be positive integers')

    if new_height == 0 and new_width == 0:
        return image
    elif new_height == 0:
        new_height = int(1 / aspect_ratio * new_width)
    elif new_width == 0:
        new_width = int(aspect_ratio * new_height)

    new_shape = (new_width, new_height)

    return cv2.resize(image, new_shape)

def resize_percentage(image, percentage=0):
    ''' Resizes an image by reducing the dimensions to the given percentage of the original

    Arguments:
        image (numPy array) -- the image to be resized

        percentage (int, optional) -- the percentage out of the original image's dimensions to
        resize to; the default value of 0 means that no resizing will be done
    '''
    image_h, image_w = image.shape[:2]
    aspect_ratio = image_w / image_h

    if percentage == 0:
        return image
    elif percentage < 0:
        raise ValueError('The "percentage" argument must be a positive integer')
    else:
        new_width = int(percentage / 100 * image_w)
        new_height = int(1 / aspect_ratio * new_width)
        new_shape = (new_width, new_height)

        return cv2.resize(image, new_shape)
