"""
Created on Thu Oct  3 19:50:10 2019

@author: Bogdan
"""
import os
import sys
import numpy as np
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils as projutils


def visible_watermark(image, extra_inputs, parameters):
    ''' Embeds a watermark image over a host image, using the visible watermarking technique; the
    watermark is scaled to the selected size and is embedded into the selected location, with the
    selected transparency

    Arguments:
        *image* (NumPy array) -- the image to be watermarked

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call

            *Watermark* (NumPy array) -- the image to be embedded on top of the host image

        *parameters* (dictionary) -- a dictionary containing following keys:

            *transparency* (str, optional) -- how will the watermark image be overlayed over the
            host image; possible values are: *opaque*, *transparent* and *very transparent*; default
            value is *transparent*

            *location* (str, optional) -- the location where the watermark image will be
            embedded; possible values are: *bottom right*, *bottom left*, *top right*, *top left*,
            *center*, *everywhere*; default value is *bottom right*

            *size* (int, optional) -- the maximum width of the watermark image, as a
            percentage of the width of the host image; possible values are: 10 to 90, with
            increments of 10; default value is 20 (%)

    Returns:
        list of NumPy array uint8 -- list containing the watermarked image

    Observations:
        If the watermark image's width is smaller than the maximum width, the image will be left
        unchanged. If the height of the watermark image (after width adjustment) is greater than the
        height of the host image, the height of the watermark image will be rescaled as to fit the
        host image
    '''
    # Load the extra parameter, the watermark image
    watermark = extra_inputs['Watermark']

    # Parameters extraction
    if 'transparency' in parameters:
        mode = parameters['transparency']
    else:
        mode = 'transparent'

    if 'location' in parameters:
        location = parameters['location']
    else:
        location = 'bottom right'

    if 'size' in parameters:
        size = parameters['size']
    else:
        size = 20

    # Check if the watermark image needs rescaling
    image_h, image_w = image.shape[:2]
    watermark_h, watermark_w = watermark.shape[:2]
    maximum_width = int(size / 100 * image_w)

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
        if image.shape[2] == 4:
            image = image[:, :, :3]

        if watermark.shape[2] == 4:
            watermark = watermark[:, :, :3]
    else:
        # Add opaque alpha channels to both images (if not already present)
        if image.shape[2] == 3:
            alpha_channel = np.ones((image_h, image_w), dtype='uint8') * 255
            image = np.dstack((image, alpha_channel))

        if watermark.shape[2] == 3:
            alpha_channel = np.ones((watermark_h, watermark_w), dtype='uint8') * 255
            watermark = np.dstack((watermark, alpha_channel))

    # Apply the watermark over the host image; alpha blending technique is used
    # result = background * (1 - alpha) + foreground * alpha
    watermarked_image = image.copy()

    # Compute the alpha level needed for alpha blending
    if mode == 'opaque':
        alpha_level = 255 / 255
    elif mode == 'transparent':
        alpha_level = 170 / 255
    elif mode == 'very transparent':
        alpha_level = 85 / 255

    # Compute the region of interest, based on the location specified by user
    if location == 'top left':
        line_start = 10
        line_end = watermark_h + 10
        column_start = 10
        column_end = watermark_w + 10
    elif location == 'top right':
        line_start = 10
        line_end = watermark_h + 10
        column_start = image_w - watermark_w - 10
        column_end = image_w - 10
    elif location == 'bottom left':
        line_start = image_h - watermark_h - 10
        line_end = image_h - 10
        column_start = 10
        column_end = watermark_w + 10
    elif location == 'bottom right':
        line_start = image_h - watermark_h - 10
        line_end = image_h - 10
        column_start = image_w - watermark_w - 10
        column_end = image_w - 10
    elif location == 'center':
        line_start = int(image_h / 2 - watermark_h / 2)
        line_end = int(image_h / 2 + watermark_h / 2)
        column_start = int(image_w / 2 - watermark_w / 2)
        column_end = int(image_w / 2 + watermark_w / 2)
    elif location == 'everywhere':
        # Compute number of horizontal and vertical repeats, respectively
        repeat_x = image_w // watermark_w
        repeat_y = image_h // watermark_h

        for x in range(repeat_x):
            for y in range(repeat_y):
                line_start = watermark_h * y
                line_end = watermark_h * (y + 1)
                column_start = watermark_w * x
                column_end = watermark_w * (x + 1)

                watermarked_image[line_start : line_end, column_start : column_end, : 3] = \
                    image[line_start : line_end, column_start : column_end, : 3] * (1 - alpha_level) + \
                    watermark[:, :, : 3] * alpha_level

        return [watermarked_image]
    else:
        raise ValueError("'location' parameter value not allowed")

    # Overlay the watermark on the host image
    watermarked_image[line_start : line_end, column_start : column_end, : 3] = \
        image[line_start : line_end, column_start : column_end, : 3] * (1 - alpha_level) + \
        watermark[:, :, : 3] * alpha_level

    return [watermarked_image]
