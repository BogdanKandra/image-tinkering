"""
Created on Sun Mar 10 15:12:37 2019

@author: Bogdan
"""
import cv2
from matplotlib import pyplot as plt
import numpy as np


def isGrayscale(image):
    """ This function takes an image as parameter and returns whether the image
    is grayscale or not
    """
    return len(image.shape) == 2
    
def isColor(image):
    """ This function takes an image as parameter and returns whether the image
    is grayscale or not
    """
    return len(image.shape) != 2

def getChannels(image):
    """ This function takes an image as parameter and returns a list containing
    its R, G, B channels or the image itself, if it is grayscale
    """
    return [image] if isGrayscale(image) else cv2.split(image)

def getFFTs(image):
    """ This function takes an image as parameter and returns a list containing
    the Fast Fourier Transforms of each of the image's channels
    """
    return [np.fft.fftshift(np.fft.fft2(channel)) for channel in getChannels(image)]

def fft_plot(image, cmap=None):
    """Takes a frequency domain image and displays its spectrum.

    Arguments:
        image (numPy array) -- the image to be displayed
        
        cmap (str) -- optional, the color map to be used; default value is None

    Returns:
        Nothing
    """
    
    # Take the magnitudes and reduce values by logarithming
    magnitudes = np.log(np.abs(image) + 1)
    
    plt.figure()
    plt.imshow(magnitudes, cmap)
    plt.show()
