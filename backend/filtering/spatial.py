'''
Created on Sat May 18 16:58:05 2019

@author: Bogdan
'''
import os
import sys
import cv2
import numpy as np
from . import helpers
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def negative(image, extra_inputs={}, parameters={}):
    '''Applies a **Negative Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    # Negative is defined as complementary to maximum intensity value
    negative_image = 255 - image

    return [negative_image]

def grayscale(image, extra_inputs={}, parameters={}):
    '''Applies a **Grayscale Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    if utils.is_grayscale(image):
        gray_image = image
    else:
        gray_image = image[:, :, 0] * 0.11 + image[:, :, 1] * 0.59 + image[:, :, 2] * 0.3
        gray_image = np.uint8(np.rint(gray_image))

    return [gray_image]

def sepia(image, extra_inputs={}, parameters={}):
    '''Applies a **Sepia Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    # Apply the Sepia formulas
    if utils.is_color(image):
        result_red = image[:, :, 2] * 0.393 + image[:, :, 1] * 0.769 + image[:, :, 0] * 0.189
        result_green = image[:, :, 2] * 0.349 + image[:, :, 1] * 0.686 + image[:, :, 0] * 0.168
        result_blue = image[:, :, 2] * 0.272 + image[:, :, 1] * 0.534 + image[:, :, 0] * 0.131
    else:
        result_red = image * 0.393 + image * 0.769 + image * 0.189
        result_green = image * 0.349 + image * 0.686 + image * 0.168
        result_blue = image * 0.272 + image * 0.534 + image * 0.131

    # Trim values greater than 255
    result_red = np.where(result_red > 255, 255, result_red)
    result_green = np.where(result_green > 255, 255, result_green)
    result_blue = np.where(result_blue > 255, 255, result_blue)

    # Round the values and convert to int
    result_red = np.uint8(np.rint(result_red))
    result_green = np.uint8(np.rint(result_green))
    result_blue = np.uint8(np.rint(result_blue))

    sepia_image = utils.merge_channels([result_blue, result_green, result_red])

    return [sepia_image]

def binarize(image, extra_inputs={}, parameters={}):
    ''' Binarizes an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be binarized

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *thresholding_Method* (str, optional) -- the type of thresholding; possible values are
            *simple* and *adaptive*; default value is *adaptive*. In the case of *simple*
            thresholding, the binarization threshold is chosen by the user and it is the same for
            all pixels; this can cause unsatisfactory results if the source image has different
            lighting conditions in different areas. In *adaptive* thresholding, the threshold is
            automatically computed and is different for each source pixel

            *threshold* (str, optional) -- the value which separates the two pixel values, in the
            case of simple thresholding; possible values are *median* and *127*; default value is
            *median*

            *maximum_Value* (int, optional) -- the value with which to replace pixel values greater
            than the threshold; default value is 255; must be between 1 and 255

            *adaptive_Method* (str, optional) -- the type of adaptive threshold computation;
            possible values are *mean* and *gaussian*; default value is *gaussian*. When *mean*,
            the threshold is computed as the mean of the values in the neighbourhood; when
            *gaussian*, the threshold is computed as a gaussian-weighted sum of the neighbourhood
            values

            *neighbourhood_Size* (int, optional) -- the square size of the neighbourhood of values
            to consider when computing adaptive thresholds; possible values are *5*, *9* and *15*;
            default value is 15
    '''
    if utils.is_color(image):
        image = grayscale(image, {}, {})[0]

    if 'thresholding_Method' in parameters:
        thresholding = parameters['thresholding_Method']
    else:
        thresholding = 'adaptive'

    if 'maximum_Value' in parameters:
        max_value = parameters['maximum_Value']
    else:
        max_value = 255

    if thresholding == 'simple':
        threshold = parameters['threshold']

        if threshold == 'median':
            threshold = np.median(image)
        else:
            threshold = 127

        # If the pixel value is greater than the threshold, set the pixel value to 'max_value'
        # Otherwise, set it to 0
        binary_image = np.where(image > threshold, max_value, 0).astype(np.uint8)
    else:
        if 'adaptive_Method' in parameters:
            method = parameters['adaptive_Method']
        else:
            method = 'gaussian'

        if 'neighbourhood_Size' in parameters:
            neighbourhood_size = parameters['neighbourhood_Size']
        else:
            neighbourhood_size = 15

        # Compute the thresholds and set the new values accordingly
        thresholds = helpers.get_thresholds(image, method, neighbourhood_size) - 2
        binary_image = np.where(image > thresholds, max_value, 0).astype(np.uint8)

    return [binary_image]

def blur(image, extra_inputs, parameters):
    '''Applies a **Blur Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *type* (str, optional) -- the type of kernel to be used; possible values are *box* and
            *gaussian*; default value is *gaussian*

            *strength* (str) -- the strength of the blur effect; possible values are *weak*,
            *medium* and *strong*

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    if 'type' in parameters:
        kernel = parameters['type']
    else:
        kernel = 'gaussian'

    strength = parameters['strength']
    if strength == 'weak':
        size = 5
    elif strength == 'medium':
        size = 11
    else:
        size = 17

    if 'backend.filtering.helpers' in sys.modules:
        module_key = 'backend.filtering.helpers'
    else:
        module_key = 'filtering.helpers'

    kernel = getattr(sys.modules[module_key], 'generate_{}_kernel'.format(kernel))(size)
    blurred_image = helpers.apply_kernel(image, kernel)

    return [blurred_image]

def sharpen(image, extra_inputs, parameters):
    ''' Applies a **Sharpen Filter** onto an image \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *type* (str, optional) -- the type of kernel to be used when performing the blur;
            possible values are *box* and *gaussian*; default value is *gaussian*

            *strength* (str) -- the strength of the blur effect; possible values are *weak*,
            *medium* and *strong*

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    if 'type' in parameters:
        kernel = parameters['type']
    else:
        kernel = 'gaussian'

    strength = parameters['strength']

    # Removing the blurred image from the original results in an image containing only the details
    # Adding the details image to the original results in a sharpened image
    blurred_image = blur(image, {}, {'type': kernel, 'strength': strength})[0]
    details_image = np.where(image - blurred_image < 0, 0, image - blurred_image)
    sharpened_image = np.where(image + details_image > 255, 255, image + details_image)

##### Alternative implementation using kernels
#    sharp_3x3_1 = np.array([[0, -1, 0],
#                            [-1, 5, -1],
#                            [0, -1, 0]])
#    sharp_3x3_2 = np.array([[-1, -1, -1],
#                            [-1, 9, -1],
#                            [-1, -1, -1]])
#    sharp_3x3_3 = np.array([[-1/8, -1/8, -1/8],
#                            [-1/8, 2, -1/8],
#                            [-1/8, -1/8, -1/8]])
    # Unsharp masking kernel
#    sharp_5x5 = np.array([[-0.00391, -0.01563, -0.02344, -0.01563, -0.00391],
#                          [-0.01563, -0.06250, -0.09375, -0.06250, -0.01563],
#                          [-0.02344, -0.09375, 1.85980, -0.09375, -0.02344],
#                          [-0.01563, -0.06250, -0.09375, -0.06250, -0.01563],
#                          [-0.00391, -0.01563, -0.02344, -0.01563, -0.00391]])
#
#    sharpened_image = apply_kernel(image, sharp_5x5)

    return [sharpened_image]

def ascii_art(image, extra_inputs, parameters):
    '''Applies an **ASCII Art Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *charset* (str, optional) -- the character set to use when rendering
            ASCII art image; possible values are *standard*, *alternate* and *full*

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    # Small, 11 character ramps
    STANDARD_CHARSET = [' ', '.', ',', ':', '-', '=', '+', '*', '#', '%', '@']  # "Standard"
    ALTERNATE_CHARSET = [' ', '.', ',', ':', '-', '=', '+', '*', '%', '@', '#']   # "Alternate"

    # Full, 70 character ramp
    FULL_CHARSET = [' ', '.', '\'', '`', '^', '"', ',', ':', ';', 'I', 'l', '!',
                    'i', '>', '<', '~', '+', '_', '-', '?', ']', '[', '}', '{',
                    '1', ')', '(', '|', '\\', '/', 't', 'f', 'j', 'r', 'x', 'n',
                    'u', 'v', 'c', 'z', 'X', 'Y', 'U', 'J', 'C', 'L', 'Q', '0',
                    'O', 'Z', 'm', 'w', 'q', 'p', 'd', 'b', 'k', 'h', 'a', 'o',
                    '*', '#', 'M', 'W', '&', '8', '%', 'B', '@', '$']

    if 'charset' in parameters:
        if parameters['charset'] == 'standard':
            CHARS = STANDARD_CHARSET
        elif parameters['charset'] == 'alternate':
            CHARS = ALTERNATE_CHARSET
        else:
            CHARS = FULL_CHARSET
    else:
        CHARS = ALTERNATE_CHARSET

    buckets = 256 / len(CHARS)
    CHARS = CHARS[::-1] # Reverse the list

    def number_to_char(number):
        return CHARS[int(number // buckets)]

    # Vectorizing this function allows it to be applied on arrays
    number_to_char = np.vectorize(number_to_char)

    # Resize and convert the image to grayscale
    h, w = image.shape[:2]
    original_size = (w, h)
    image = utils.resize_dimension(image, new_width=80)
    if utils.is_color(image):
        image = grayscale(image)[0]

    # Build results as list of lines of text and entire text
    lines = [''.join(number_to_char(row)) for row in list(image)]
    text_spaceless = ''.join(lines)

    # Determine the widest letter, to account for the rectangular aspect ratio of the characters
    font_face = cv2.FONT_HERSHEY_PLAIN
    font_scale = 1
    thickness = 1
    size, base_line = cv2.getTextSize('.', font_face, font_scale, thickness)
    maximum_letter_width = size[0]

    for i in range(len(text_spaceless)):
        letter_width = cv2.getTextSize(text_spaceless[i], font_face, font_scale, thickness)[0][0]
        if letter_width > maximum_letter_width:
            maximum_letter_width = letter_width

    # Create resulting image as white and write text on it
    number_of_lines = len(lines)
    number_of_cols = len(lines[0]) * maximum_letter_width
    dy = 14 # Vertical offset to account for the characters height
    ascii_image = np.zeros((number_of_lines * dy, number_of_cols), np.uint8)
    ascii_image[:, :] = 255

    for i, line in enumerate(lines):
        y = i * dy
        for j, char in enumerate(line):
            cv2.putText(ascii_image, char, (j * maximum_letter_width, y), font_face, 1, \
                        (0, 0, 0), 1, lineType=cv2.FILLED)

    # Resize resulting image to original size of input image
    ascii_image = cv2.resize(ascii_image, original_size, interpolation=cv2.INTER_AREA)

    return [ascii_image]

def edge(image, extra_inputs, parameters):
    '''Performs edge detection onto an image and returns the edge image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *method* (str) -- the type of edge detection algorithm to be applied; possible values
            are *canny* and *laplacian*

            *pre-blur* (str, optional) -- whether to apply blur to the input image before convolving
            with the laplacian kernel; possible values are 'Yes' and 'No'; default value is 'Yes'

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    # Parameters extraction
    method = parameters['method']

    if 'pre-blur' in parameters:
        pre_blur = parameters['pre-blur']
        if pre_blur == 'Yes':
            pre_blur = True
        else:
            pre_blur = False
    else:
        pre_blur = True

    # Perform Edge Detection
    if method == 'canny':       # This method assumes applying the Canny Edge Detection algorithm
        pass
    elif method == 'laplacian': # This method assumes convolving the image with the Laplacian kernel
        # Preprocess the input image
        if pre_blur:
            gray = grayscale(image, {}, {})[0]
            blur_kernel = helpers.generate_gaussian_kernel(3, 1)
            processed_image = helpers.apply_kernel(gray, blur_kernel)
        else:
            processed_image = grayscale(image, {}, {})[0]

        # Convolve processed image with laplacian kernel
        laplacian_kernel_alt = np.array([[-1, -1, -1],
                                         [-1, 8, -1],
                                         [-1, -1, -1]])
#       ### Original Laplacian kernel -- gives weaker edges
#                edge_kernel_og = np.array([[0, -1, 0],
#                                           [-1, 4, -1],
#                                           [0, -1, 0]])

        edges_image = helpers.apply_kernel(processed_image, laplacian_kernel_alt)

    return [edges_image]
