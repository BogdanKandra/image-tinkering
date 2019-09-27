"""
Created on Sat May 18 16:58:05 2019

@author: Bogdan
"""
import os
import sys
import cv2
import numpy as np
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def negative(image, extra_inputs={}, parameters={}):
    """Applies a **Negative Filter** on an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    """
    # Negative is defined as complementary to maximum intensity value
    negative_image = 255 - image

    return [negative_image]

def grayscale(image, extra_inputs={}, parameters={}):
    """Applies a **Grayscale Filter** on an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    """
    if utils.is_grayscale(image):
        gray_image = image
    else:
        gray_image = image[:, :, 0] * 0.11 + image[:, :, 1] * 0.59 + image[:, :, 2] * 0.3
        gray_image = np.uint8(np.rint(gray_image))

    return [gray_image]

def sepia(image, extra_inputs={}, parameters={}):
    """Applies a **Sepia Filter** on an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    """
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

    sepia_image = cv2.merge((result_blue, result_green, result_red))

    return [sepia_image]

def ascii_art(image, extra_inputs, parameters):
    """Applies an **ASCII Art Filter** on an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *charset* (str, optional) -- the character set to use when rendering
            ASCII art image; possible values are *standard*, *alternate* and *full*

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    """
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
    image = utils.resize(image)
    if utils.is_color(image):
        image = grayscale(image)

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
