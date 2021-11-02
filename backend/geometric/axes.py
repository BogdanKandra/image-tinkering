"""
Created on Fri May 17 17:39:42 2019

@author: Bogdan
"""
import numpy as np


def flip(image, extra_inputs, parameters):
    """ Flips an image along the horizontal, vertical axis or both.

    Arguments:
        *image* (NumPy array) -- the image to flip

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs
        for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *axis* (str, optional) -- the axis along which to flip the image;
            possible values are *horizontal*, *vertical* and *both*; default
            value is *horizontal*

    Returns:
        list of NumPy array uint8 -- list containing the flipped image
    """
    if 'axis' in parameters:
        axis = parameters['axis']
    else:
        axis = 'horizontal'

    flipped_image = np.zeros(image.shape, dtype=np.uint8)
    if axis == 'vertical':
        for i in range(image.shape[0]):
            flipped_image[i] = image[image.shape[0] - i - 1]
        # flipped_image = np.flipud(image)
    elif axis == 'horizontal':
        for j in range(image.shape[1]):
            flipped_image[:, j] = image[:, image.shape[1] - j - 1]
        # flipped_image = np.fliplr(image)
    else:
        # Flip vertically
        result_temp = np.zeros(image.shape, dtype=np.uint8)
        for i in range(image.shape[0]):
            result_temp[i] = image[image.shape[0] - i - 1]

        # Flip horizontally
        for j in range(image.shape[1]):
            flipped_image[:, j] = result_temp[:, image.shape[1] - j - 1]

        # flipped_image = np.fliplr(image)
        # flipped_image = np.flipud(flipped_image)

    return [flipped_image]

def mirror(image, extra_inputs, parameters):
    """ Mirrors an image along the horizontal, vertical axis or both and pastes
    the result besides the original image, in the desired location.

    Arguments:
        *image* (NumPy array) -- the image to mirror

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs
        for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *axis/location* (str, optional) -- specifies the axis along which
            to flip the image; also, the location where the flipped image will
            be pasted. Possible values are *horizontal/left*, *horizontal/right*,
            *vertical/top*, *vertical/bottom*, *both/left/top*, *both/left/bottom*,
            *both/right/top*, *both/right/bottom*; default value is *horizontal/right*

    Returns:
        list of NumPy array uint8 -- list containing the mirrored image
    """
    if 'axis/location' in parameters:
        components = parameters['axis/location'].split('/')
        axis = components[0]
        if axis == 'both':
            location_h = components[1]
            location_v = components[2]
        else:
            location = components[1]
    else:
        axis = 'horizontal'
        location = 'right'

    # Use the flip function to flip the input image accordingly
    if axis != 'both':
        flipped_image = flip(image, {}, {'axis': axis})[0]

        # Create the mirror image according to the location parameter
        if location == 'left':
            mirror_image = np.hstack((flipped_image, image))
        elif location == 'right':
            mirror_image = np.hstack((image, flipped_image))
        elif location == 'top':
            mirror_image = np.vstack((flipped_image, image))
        else:
            mirror_image = np.vstack((image, flipped_image))
    else:
        flipped_h = flip(image, {}, {'axis': 'horizontal'})[0]
        flipped_v = flip(image, {}, {'axis': 'vertical'})[0]
        flipped_both = flip(flipped_v, {}, {'axis': 'horizontal'})[0]

        # Create the mirror image according to the location parameter
        if location_h == 'left':
            mirror1 = np.hstack((flipped_h, image))
            mirror2 = np.hstack((flipped_both, flipped_v))
        else:
            mirror1 = np.hstack((image, flipped_h))
            mirror2 = np.hstack((flipped_v, flipped_both))

        if location_v == 'top':
            mirror_image = np.vstack((mirror2, mirror1))
        else:
            mirror_image = np.vstack((mirror1, mirror2))

    return [mirror_image]
