"""
Created on Sun Mar 10 15:12:37 2019

@author: Bogdan
"""
import cv2
from matplotlib import pyplot as plt
import numpy as np
import pickle
import time


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

def testProcessingSpeed(path):
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    start = time.time()
    gray = isGrayscale(image)
    end = time.time()
    print('Gray:', end - start)

    start = time.time()
    color = isColor(image)
    end = time.time()
    print('Color:', end - start)

    start = time.time()
    channels = getChannels(image)
    end = time.time()
    print('Channels:', end - start)

    start = time.time()
    ffts = getFFTs(image)
    end = time.time()
    print('FFTs:', end - start, '\n')

def fft_plot(image, cmap=None):
    """Takes an image, computes its FFT and displays both using pyplot.

    Arguments:
        image (numPy array) -- the image to be transformed
        
        cmap (str) -- optional, the color map to be used; default value is None

    Returns:
        Nothing
    """
    
    magnitudes = np.log(np.abs(image) + 1)
    
    plt.figure()
    plt.imshow(magnitudes, cmap)
    plt.show()


if __name__ == '__main__':
    
    impath1 = '../webui/static/testinputs/flag.jpg'
    impath2 = '../webui/static/testinputs/elaine.tiff'
    impath3 = '../webui/static/testinputs/brontosaur.jpg'
    impath4 = '../webui/static/testinputs/lena.tiff'

    image = cv2.imread(impath3, cv2.IMREAD_UNCHANGED)

#    testProcessingSpeed(impath1)
#    testProcessingSpeed(impath2)
#    testProcessingSpeed(impath3)
#    testProcessingSpeed(impath4)
    
#    picklePath = 'brontosaur_15530789941596785_fft.pickle'
#    f = open(picklePath, 'rb')
#    im = pickle.load(f)
#    f.close()
#    fft_plot(im)

#    cv2.imshow('Image', image)

    cv2.waitKey()
    cv2.destroyAllWindows()
