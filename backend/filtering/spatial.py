"""
Created on Sat May 18 16:58:05 2019

@author: Bogdan
"""
import os, sys
import cv2
import numpy as np
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(projectPath)
from backend import utils


def negative(image, parameters={}):
    """Applies a **Negative Filter** on an image. \n
    
    Arguments:
        *image* (NumPy array) -- the image to be filtered
        
        *parameters* (dictionary) -- an empty parameter dictionary
        
    Returns:
        NumPy array uint8 -- the filtered image
    """
    # Negative is defined as complementary to maximum intensity value
    negative_image = 255 - image
    
    return negative_image

def grayscale(image, parameters={}):
    """Applies a **Grayscale Filter** on an image. \n
    
    Arguments:
        *image* (NumPy array) -- the image to be filtered
        
        *parameters* (dictionary) -- an empty parameter dictionary
    
    Returns:
        NumPy array uint8 -- the filtered image
    """
    if utils.isGrayscale(image):
        gray_image = image
    else:
        gray_image = image[:,:,0] * 0.11 + image[:,:,1] * 0.59 + image[:,:,2] * 0.3
        gray_image = np.uint8(np.rint(gray_image))
    
    return gray_image

def sepia(image, parameters={}):
    """Applies a **Sepia Filter** on an image. \n
    
    Arguments:
        *image* (NumPy array) -- the image to be filtered
        
        *parameters* (dictionary) -- an empty parameter dictionary
        
    Returns:
        NumPy array uint8 -- the filtered image    
    """
    # Apply the Sepia formulas
    if utils.isColor(image):
        result_red = image[:,:,2] * 0.393 + image[:,:,1] * 0.769 + image[:,:,0] * 0.189
        result_green = image[:,:,2] * 0.349 + image[:,:,1] * 0.686 + image[:,:,0] * 0.168
        result_blue = image[:,:,2] * 0.272 + image[:,:,1] * 0.534 + image[:,:,0] * 0.131
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
    
    return sepia_image

def ascii_art(image, parameters={}):
    """Applies an **ASCII Art Filter** on an image. \n
    
    Arguments:
        *image* (NumPy array) -- the image to be filtered
        
        *parameters* (dictionary) -- a dictionary containing following keys:
            
            *TBD*
            
    Returns:
        NumPy array uint8 -- the filtered image
    """
    # Vars and params
    #CHARS = ['.', ',', ':', ';', '+', '*', '?', '%', 'S', '#', '@']
    #CHARS = [' ', ',', '.', ':', '-', '=', '+', '*', '#', '%', '@']
    CHARS = [' ', ',', '.', ':', '-', '=', '+', '*', '%', '@', '#']
    CHARS = CHARS[::-1] # Reverse the list
    buckets = 25
    
    def numberToChar(number):
        return CHARS[number // buckets]
    
    # Vectorizing this function allows it to be applied on arrays
    numberToChar = np.vectorize(numberToChar)
    
    # Resize and convert the image to grayscale
    h, w = image.shape[:2]
    original_size = (w, h)
    image = utils.resize(image)
    if utils.isColor(image):
        image = grayscale(image)
    
    # Build results as list of lines of text and entire text
    lines = [''.join(numberToChar(row)) for row in list(image)]
    textSpaceless = ''.join(lines)
    
    # Determine the widest letter, to account for the rectangular aspect ratio of the characters
    font_face = cv2.FONT_HERSHEY_PLAIN
    font_scale = 1
    thickness = 1
    size, base_line = cv2.getTextSize('.', font_face, font_scale, thickness)
    maximum_letter_width = size[0]
    
    for i in range(len(textSpaceless)):
        letter_width = cv2.getTextSize(textSpaceless[i], font_face, font_scale, thickness)[0][0]
        if letter_width > maximum_letter_width:
            maximum_letter_width = letter_width
    
    # Create resulting image as white and write text on it
    numberOfLines = len(lines)
    numberOfCols = len(lines[0]) * maximum_letter_width
    dy = 14 # Vertical offset to account for the characters height
    ascii_image = np.zeros((numberOfLines * dy, numberOfCols), np.uint8)
    ascii_image[:,:] = 255

    for i, line in enumerate(lines):
        y = i * dy
        for j, char in enumerate(line):
            cv2.putText(ascii_image, char, (j * maximum_letter_width, y), font_face, 1, (0,0,0), 1, lineType=cv2.FILLED)
    
    # Display resulting image
    ascii_image = cv2.resize(ascii_image, original_size, interpolation=cv2.INTER_AREA)

    return ascii_image
