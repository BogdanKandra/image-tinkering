"""
Created on Thu Oct  3 19:50:10 2019

@author: Bogdan
"""
import os
import sys
import numpy as np
import cv2
import utils as wmutils
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils as projutils


def visible_watermark(image, extra_inputs, parameters):
    ''' Embeds a watermark image into the bottom-right corner of a host image,
    using the visible watermarking technique

    Arguments:
        *image* (NumPy array) -- the image to be watermarked

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call

            *watermark image* (NumPy array) -- the image to be embedded on top of the host image

        *parameters* (dictionary) -- a dictionary containing following keys:

            *Blending Mode* (str, optional) -- how will the watermark image be overlayed over the
            host image; possible values are: *transparent* and *opaque*; default value is
            *transparent*

            *Watermark Location* (str, optional) -- the location where the watermark image will be
            embedded; possible values are: *bottom right*, *bottom left*, *top right*, *top left*,
            *center*, *everywhere*; default value is *bottom right*

            *Watermark Size* (int, optional) -- the maximum width of the watermark image, as a
            percentage of the width of the host image; possible values are: 10 to 100, with
            increments of 10; default value is 10 (%)

    **Notes**: if the watermark image's width is smaller than the maximum width, the image will be
    left unchanged. If the height of the watermark image (after width adjustment) is greater
    than the height of the host image, the height of the watermark image will be rescaled as to fit
    the host image

    Returns:
        list of NumPy array uint8 -- list containing the watermarked image
    '''
    # Load the extra parameter, the watermark image
    watermark = extra_inputs['watermark image']

    # Parameters extraction
    if 'Blending Mode' in parameters:
        mode = parameters['Blending Mode']
    else:
        mode = 'transparent'

    if 'Watermark Location' in parameters:
        location = parameters['Watermark Location']
    else:
        location = 'bottom right'

    if 'Watermark Size' in parameters:
        size = parameters['Watermark Size']
    else:
        size = 10

    # Check if the watermark image needs rescaling
    image_h, image_w = image.shape[:2]
    watermark_h, watermark_w = watermark.shape[:2]
    maximum_width = size / 100 * image_w

    if watermark_w > maximum_width: # Resize watermark image by new width
        watermark = projutils.resize_dimension(watermark, new_width=maximum_width)
        watermark_h, watermark_w = watermark.shape[:2] # The watermark dimensions need to be updated

    if watermark_h > image_h:       # Resize watermark image by height of host image
        watermark = projutils.resize_dimension(watermark, new_height=image_h)

    # If any of the images are grayscale, convert them to the color equivalent
    if projutils.is_grayscale(image):
        image = projutils.merge_channels([image, image, image])

    if projutils.is_grayscale(watermark):
        watermark = projutils.merge_channels([watermark, watermark, watermark])

    # Verify whether the alpha channel is needed or not and act accordingly
    if mode == 'opaque':
        # Remove the alpha channels from both images (if present)
        pass
    else:
        # Add alpha channels to both images (if not already present)
        pass
    
    # TODO - Apply the watermark using the equations

def visible_watermark1(wmImage, hostImage):
    # Split the image channels and merge them back using the Alpha Channel as a
    # mask, due to a bug in OpenCV representing the supposed transparent pixels 
    # (0-valued) as opaque pixels (255-valued)
    (B, G, R, A) = cv2.split(wmImage)
    B = cv2.bitwise_and(B, B, mask=A)  # Performs the and operation only for elems
    G = cv2.bitwise_and(G, G, mask=A)  # where A[i][j] != 0, thus making the correct
    R = cv2.bitwise_and(R, R, mask=A)  # pixels completely transparent (equal to 0)
    wmImage = cv2.merge([B, G, R, A])
    
    wmH, wmW = wmImage.shape[:2]
    
    # Add an extra dimension to the host image - the alpha channel
    imageH, imageW = hostImage.shape[:2]
    alpha = np.ones((imageH, imageW), dtype='uint8') * 255
    hostImage = np.dstack((hostImage, alpha))
    
    # Build an overlay of the same size as the host image
    overlay = np.zeros((imageH, imageW, 4), dtype='uint8')
    
    # Add the watermark image to the overlay in the bottom-right corner
    overlay[imageH - wmH - 10:imageH - 10, imageW - wmW - 10:imageW - 10] = wmImage
    
    # Add the overlay to the host image and save into output
    output = hostImage.copy()
    cv2.addWeighted(overlay, 1, hostImage, 1, 0, output)
    
    return output
