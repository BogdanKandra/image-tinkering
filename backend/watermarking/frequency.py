"""
Created on Thu Oct  3 19:51:06 2019

@author: Bogdan
"""
import os
import sys
import numpy as np
import cv2
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def fft_watermark_embed(image, extra_inputs, parameters):
    ''' Embeds a watermark image into a host image, using the Fast Fourier Transform

    Arguments:
        *image* (NumPy array) -- the image to be watermarked

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call

            *Watermark* (NumPy array) -- the image to be embedded into the host image

        *parameters* (dictionary) -- a dictionary containing following keys:

            *alpha* (float) -- the embedding strength factor

    Returns:
        list of NumPy array float64 -- list containing the watermarked image (float, but converted
        to int when saved)
    '''
    # Load the extra parameter, the watermark image
    watermark = extra_inputs['Watermark']

    # Parameters extraction
    alpha = parameters['alpha']

    # Resize the watermark image to the shape of the host image
    image_h, image_w = image.shape[:2]
    watermark_h, watermark_w = watermark.shape[:2]

    if watermark_h > image_h or watermark_w > image_w: # Scale down the watermark image
        watermark = utils.resize_dimension(watermark, image_h, image_w)
    else:
        watermark = utils.resize_dimension(watermark, image_h, image_w)

    watermark_h, watermark_w = watermark.shape[:2] # Recompute the watermark dimensions

    # Take the FFT of the host and watermark images and center them
    image_fft = np.fft.fftshift(np.fft.fft2(image))
    watermark_fft = np.fft.fftshift(np.fft.fft2(watermark))

    # Watermark the host image using the frequency domain
    result_fft = image_fft + alpha * watermark_fft
    
    # Take its Inverse FFT and convert the resulting values into floats
    result_image = np.fft.ifft2(np.fft.ifftshift(result_fft)) # dtype = 'complex128'
    result_image = np.real(result_image)

    return result_image




