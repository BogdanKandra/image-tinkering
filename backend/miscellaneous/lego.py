"""
Created on Wed Oct 30 16:57:19 2019

@author: Bogdan
"""
import json
import os
import pickle
import sys
import numpy as np
import cv2
from scipy.spatial.distance import cdist
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend.filtering.spatial import grayscale
from backend import utils


def get_closest_usable_tile_index(distances, tile_usage_grid, line, column):
    ''' Helper function which returns the index of the closest tile which has
    not been used on a square centered on the current position, of radius 1 '''
    grid_height, grid_width = tile_usage_grid.shape

    while True:
        closest_tile_index = np.argwhere(distances == np.min(distances))[0][-1]
        found = True

        for i in range(line-1, line+1):
            for j in range(column-1, column+2):
                if i >= 0 and j >= 0 and i < grid_height and j < grid_width and (i != line or j < column):
                    if tile_usage_grid[i][j] == closest_tile_index:
                        found = False
                        break
            if not found:
                distances = np.delete(distances, np.argwhere(distances == np.min(distances)))
                break

        if found:
            return closest_tile_index

def get_closest_ral_colour(rgb_list):
    ''' Function takes a standard RGB colour as argument, computes and returns
    the closest RAL colour '''
    # Read the JSON file containing mappings between the RAL colours and their RGB representation
    ral_mappings_path = os.path.join(project_path, 'webui', 'static', 'config', 'ral_colours.json')

    with open(ral_mappings_path, 'r') as ral_file:
        ral_mappings = json.load(ral_file)

        # Compute distances between our colour and all RAL colours
        our_colour = np.array(rgb_list).reshape((1, 3))
        ral_colours = np.zeros((len(ral_mappings), 3))
        ral_mappings_keys = list(ral_mappings.keys())
        
        for index, colour_id in enumerate(ral_mappings.keys()):
            ral_colours[index] = np.array(ral_mappings[colour_id])
        
        distances = cdist(our_colour, ral_colours)
        closest_ral_index = np.where(distances == np.min(distances))[1][0]
        closest_ral_key = ral_mappings_keys[closest_ral_index]
        
    return ral_mappings[closest_ral_key]

def build_mosaic(image, technique, alpha_level, resolution, redundancy):
    ''' Helper function which actually builds the mosaic '''
    if utils.is_grayscale(image):
        image = utils.merge_channels([image, image, image])

    database_path = os.path.join(project_path, 'backend', 'miscellaneous', 'database')
    pickle_name = 'cakes_' + resolution + '.pickle'
    pickle_path = os.path.join(database_path, pickle_name)

    with open(pickle_path, 'rb') as p:
        tiles_height, tiles_width = pickle.load(p)
        tiles_averages_dict = pickle.load(p)

    tiles_averages = np.zeros((len(tiles_averages_dict), 3))
    tiles_averages_values = list(tiles_averages_dict.values())
    tiles_averages_keys = list(tiles_averages_dict.keys())
    for i in range(len(tiles_averages_dict)):
        tiles_averages[i] = np.array(tiles_averages_values[i])

    image_height, image_width = image.shape[:2]

    mosaic_lines = int(image_height / tiles_height)
    mosaic_columns = int(image_width / tiles_width)
    mosaic_image = np.zeros((mosaic_lines * tiles_height, mosaic_columns * tiles_width, 3), dtype='uint8')
    tile_usage_grid = np.ones((mosaic_lines, mosaic_columns), dtype='uint8') * -1

    # For each block:
    #    Compute the average r, g, b values of the block and put them in a vector
    #    Compute the distance between the avg vector of the block and each of the avg vectors of the tiles
    #    Replace the current block with the tile located at the shortest distance from the block
    block_averages = np.zeros((1, 3))
    for line in range(mosaic_lines):
        for column in range(mosaic_columns):
            block = image[line * tiles_height : (line + 1) * tiles_height, column * tiles_width : (column + 1) * tiles_width]
            block_averages[0] = np.array((np.mean(block[:, :, 0]), np.mean(block[:, :, 1]), np.mean(block[:, :, 2])))
            distances = cdist(block_averages, tiles_averages)

            # Determine the index of the closest compatible tile
            if redundancy:
                closest_tile_index = np.where(distances == np.min(distances))[1][0]
            else:
                closest_tile_index = get_closest_usable_tile_index(distances, tile_usage_grid, line, column)

            closest_tile_name = tiles_averages_keys[closest_tile_index]
            closest_tile = cv2.imread(os.path.join(database_path, 'cakes_' + resolution, closest_tile_name), cv2.IMREAD_UNCHANGED)
            mosaic_image[line * tiles_height : (line + 1) * tiles_height, column * tiles_width : (column + 1) * tiles_width] = closest_tile
            tile_usage_grid[line][column] = closest_tile_index

    if technique == 'alternative':
        # Overlay the mosaic on the input image
        image_copy = utils.resize_dimension(image, *mosaic_image.shape[:2])
        mosaic_image = image_copy * (1 - alpha_level) + mosaic_image * alpha_level

    return mosaic_image

def ascii_art(image, extra_inputs, parameters):
    '''Applies an **ASCII Art Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for
        the call (empty)

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
                    '*', '#', 'M', 'W', '&', '8', '%', 'B', '$', '@']

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

def photomosaic(image, extra_inputs, parameters):
    ''' Builds a photomosaic which approximates the given image, using the
    database image tiles.

    Arguments:
        *image* (NumPy array) -- the image to be approximated by a photo mosaic

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for
        the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *technique* (str, optional) -- the technique used when building the
            photomosaic; possible values are *original* and *alternative*;
            default value is *original*

            *transparency* (str, optional) -- the level of transparency of the
            mosaic image; possible values are *high*, *medium* and *low*; this
            parameter is ignored unless *technique* == *alternative*; default
            value is *high*

            *resolution* (str, optional) -- the resolution of the photomosaic;
            possible values are *low*, *standard* and *high*; default value is
            *standard*

            *redundancy* (str, optional) -- whether or not to allow the same
            tile to be repeated for neighbours; possible values are *allowed*
            and *not allowed*; default value is *allowed*

    Returns:
        list of NumPy array uint8 -- list containing the photomosaic of the image
    '''
    # Parameters extraction
    if 'technique' in parameters:
        technique = parameters['technique']
    else:
        technique = 'original'

    if 'transparency' in parameters:
        transparency = parameters['transparency']
    else:
        transparency = 'high'

    if 'resolution' in parameters:
        resolution = parameters['resolution']
    else:
        resolution = 'standard'

    if 'redundancy' in parameters:
        redundancy = parameters['redundancy']
        if redundancy == 'allowed':
            redundancy = True
        else:
            redundancy = False
    else:
        redundancy = True

    # Determine the pickle to be loaded based on requested resolution
    if resolution == 'low':
        resolution = '36x20'
    elif resolution == 'standard':
        resolution = '18x10'
    elif resolution == 'high':
        resolution = '9x5'

    # Determine the alpha level needed for alpha blending, if alternative technique is required
    alpha_level = None
    if technique == 'alternative':
        if transparency == 'low':
            alpha_level = 205 / 255
        elif transparency == 'medium':
            alpha_level = 150 / 255
        elif transparency == 'high':
            alpha_level = 75 / 255

    mosaic_image = build_mosaic(image, technique, alpha_level, resolution, redundancy)

    return [mosaic_image]

def pixelate(image, extra_inputs, parameters):
    ''' Uses a form of downscaling in order to achieve an 8-bit-like filter
    appearance of an image.

    Arguments:
        *image* (NumPy array) -- the image to be pixelated

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for
        the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *fidelity* (str, optional) -- how close the resulting image will
            look compared to the original (inverse proportional to the size of
            the composing pixels); possible values are *very low*, *low*,
            *standard*, *high* and *very high*; default value is *standard*
            
            *colour_Space* (str, optional) -- the colour space used to represent
            the pixelated image; possible values are *RGB* and *RAL*; default
            value is *RGB*
    Returns:
        list of NumPy array uint8 -- list containing the pixelated image
    '''
    # Parameters extraction
    if 'fidelity' in parameters:
        resolution = parameters['fidelity']
    else:
        resolution = 'standard'
    
    if 'colour_Space' in parameters:
        space = parameters['colour_Space']
    else:
        space = 'RGB'

    # Determine the resolution of the pixel-blocks used (the length of the square)
    if resolution == 'very low':
        resolution = 25
    elif resolution == 'low':
        resolution = 20
    elif resolution == 'standard':
        resolution = 15
    elif resolution == 'high':
        resolution = 10
    elif resolution == 'very high':
        resolution = 5
    elif resolution == 'ultra high':
        resolution = 3

    # Determine the number of pixel-blocks to be used for both dimensions
    image_height, image_width = image.shape[:2]
    lines_count = image_height // resolution
    columns_count = image_width // resolution

    if utils.is_color(image):
        channels_count = image.shape[2]
        pixel_tile = np.zeros((resolution, resolution, channels_count))
        pixelated_image = np.zeros((lines_count * resolution, columns_count * resolution, channels_count), dtype='uint8')
    else:
        pixel_tile = np.zeros((resolution, resolution))
        pixelated_image = np.zeros((lines_count * resolution, columns_count * resolution), dtype='uint8')

    # For each block:
    #    Compute the average r, g, b values of the block and put them in a vector
    #    Replace the current block with a tile coloured the same as the average vector
    #    If using the RAL colour space, the determined colour is converted to RAL
    for line in range(lines_count):
        for column in range(columns_count):
            block = image[line * resolution : (line + 1) * resolution, column * resolution : (column + 1) * resolution]
            if utils.is_color(image):
                colour_used = []
                for i in range(channels_count):
                    colour_component = int(round(np.mean(block[:, :, i])))
                    colour_used.append(colour_component)
                    pixel_tile[:, :, i] = colour_component

                # Convert RGB colour to closest RAL colour if needed
                if space == 'RAL':
                    ral_colour = get_closest_ral_colour(colour_used)
                    for i in range(3):
                        pixel_tile[:, :, i] = ral_colour[i]
            else:
                pixel_tile = int(round(np.mean(block)))

            pixelated_image[line * resolution : (line + 1) * resolution, column * resolution : (column + 1) * resolution] = pixel_tile

    return [pixelated_image]

def collage():
    ''' Google "photo collage maker" '''
    pass # TODO
