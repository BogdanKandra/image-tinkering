'''
Created on Sat May 18 16:58:05 2019

@author: Bogdan
'''
import os
import sys
import cv2
import numpy as np
from scipy.signal import convolve2d
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def apply_kernel(image, kernel):
    ''' Performs convolution between the given image and kernel and returns the result '''
    if utils.is_color(image):
        result_b = convolve2d(image[:,:,0], kernel, mode='same').astype(np.uint8)
        result_g = convolve2d(image[:,:,1], kernel, mode='same').astype(np.uint8)
        result_r = convolve2d(image[:,:,2], kernel, mode='same').astype(np.uint8)

        filtered_image = utils.merge_channels([result_b, result_g, result_r])
    else:
        filtered_image = convolve2d(image, kernel, mode='same').astype(np.uint8)

    return filtered_image

def generate_box_kernel(size):
    ''' Generates a kernel having the given size and giving equal weights to all elements
    surrounding the current pixel '''
    return (1 / size ** 2) * np.ones((size, size), dtype=np.uint8)

def generate_gaussian_kernel(size, sigma=3):
    ''' Generates an one-sum kernel having the given size, containing samples from a gaussian
    distribution having the given standard deviation '''
    size = size // 2
    x, y = np.mgrid[-size : size + 1, -size : size + 1]
    normal = 1 / (2.0 * np.pi * sigma**2)
    g = np.exp(-((x ** 2 + y ** 2) / (2.0 * sigma ** 2))) * normal
    g = g / (np.sum(g))    # Normalize the kernel so the sum of elements is 1

    return g

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

    kernel = getattr(sys.modules[__name__], 'generate_{}_kernel'.format(kernel))(size)
    blurred_image = apply_kernel(image, kernel)

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
    blurred_image = blur(image, {}, {'type': kernel, 'strength': strength})[0]
    underflow_mask = image < blurred_image
    details_image = np.where(underflow_mask, 0, image - blurred_image)

    # Adding the details image to the original results in a sharpened image
    overflow_mask = image > 255 - details_image
    sharpened_image = np.where(overflow_mask, 255, image + details_image)

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
