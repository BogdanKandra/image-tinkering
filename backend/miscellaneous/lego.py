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
    ''' Function takes a standard RGB colour as argument, computes the closest
    RAL space colour and returns its code and value '''
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

    return closest_ral_key, ral_mappings[closest_ral_key]

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
            *standard*, *high*, *very high* and *ultra high*; default value is
            *standard*

    Returns:
        list of NumPy array uint8 -- list containing the pixelated image
    '''
    # Parameters extraction
    if 'fidelity' in parameters:
        resolution = parameters['fidelity']
    else:
        resolution = 'standard'

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
            else:
                pixel_tile = int(round(np.mean(block)))

            pixelated_image[line * resolution : (line + 1) * resolution, column * resolution : (column + 1) * resolution] = pixel_tile

    return [pixelated_image]

def pixelate_ral(image, extra_inputs, parameters):
    ''' A modified version of the pixelate operation, used for converting images
    into a version suitable for mosaicing. The colour representation used is a
    subset of RGB called RAL, a standard used for paint colours. In addition, a
    text file containing extra information is created.

    Arguments:
        *image* (NumPy array) -- the image to be pixelated

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for
        the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the pixelated image
    '''
    # Initialisations; constants are measured in centimeters
    tile_size = 3
    mosaic_width = 190
    mosaic_height = 250

    image_height, image_width = image.shape[:2]
    lines_count = mosaic_height // tile_size
    columns_count = mosaic_width // tile_size

    assert image_height // lines_count == image_width // columns_count
    resolution = image_height // lines_count

    # Configure the text to be used for writing
    font_face = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 0.6
    thickness = 1
    upscaling_factor = 6

    if utils.is_color(image):
        channels_count = image.shape[2]
        pixel_tile = np.zeros((resolution * upscaling_factor, resolution * upscaling_factor, channels_count))
        grid_tile = np.zeros((resolution * upscaling_factor, resolution * upscaling_factor, channels_count))
        pixelated_image = np.zeros((lines_count * resolution * upscaling_factor, columns_count * resolution * upscaling_factor, channels_count), dtype='uint8')
        grid_image = np.zeros((lines_count * resolution * upscaling_factor, columns_count * resolution * upscaling_factor, channels_count), dtype='uint8')
        colours_frequencies = {}
    else:
        pixel_tile = np.zeros((resolution * upscaling_factor, resolution * upscaling_factor))
        grid_tile = np.zeros((resolution * upscaling_factor, resolution * upscaling_factor))
        pixelated_image = np.zeros((lines_count * resolution * upscaling_factor, columns_count * resolution * upscaling_factor), dtype='uint8')
        grid_image = np.zeros((lines_count * resolution * upscaling_factor, columns_count * resolution * upscaling_factor), dtype='uint8')

    # For each block:
    #    Compute the average r, g, b values of the block and put them in a vector
    #    Replace the current block with a tile coloured as the closest RAL colour
    #    in relation to the average vector
    for line in range(lines_count):
        for column in range(columns_count):
            block = image[line * resolution : (line + 1) * resolution,
                          column * resolution : (column + 1) * resolution]
            if utils.is_color(image):
                colour_used = []
                for i in range(channels_count):
                    colour_component = int(round(np.mean(block[:, :, i])))
                    colour_used.append(colour_component)

                # Convert RGB colour to closest RAL colour and record its use
                ral_code, ral_colour = get_closest_ral_colour(colour_used)

                if ral_code in colours_frequencies:
                    colours_frequencies[ral_code] += 1
                else:
                    colours_frequencies[ral_code] = 1

                # Set the pixel tile and the grid tile
                for i in range(channels_count):
                    pixel_tile[:, :, i] = ral_colour[i]

                grid_tile[:, :, :] = 255
                grid_tile[0, :, :] = 0
                grid_tile[-1, :, :] = 0
                grid_tile[:, 0, :] = 0
                grid_tile[:, -1, :] = 0

                # Write the colour code in the center of the tile
                text_size = cv2.getTextSize(ral_code, font_face, font_scale, thickness)[0]
                text_x = (resolution * upscaling_factor - text_size[0]) // 2
                text_y = (resolution * upscaling_factor + text_size[1]) // 2
                cv2.putText(grid_tile, ral_code, (text_x, text_y), font_face, font_scale, (0, 0, 0), thickness)
            else:
                pixel_tile = int(round(np.mean(block)))

            pixelated_image[line * resolution * upscaling_factor : (line + 1) * resolution * upscaling_factor, column * resolution * upscaling_factor : (column + 1) * resolution * upscaling_factor] = pixel_tile
            grid_image[line * resolution * upscaling_factor : (line + 1) * resolution * upscaling_factor, column * resolution * upscaling_factor : (column + 1) * resolution * upscaling_factor] = grid_tile

    # Write colour usage information into a file
    tempdata_path = os.path.join(project_path, 'webui', 'static', 'tempdata')
    with open(os.path.join(tempdata_path, 'ral_info.txt'), 'w') as f:
        f.write('INFORMATII MOZAIC:\n')
        f.write('==============================\n')
        f.write('NUMAR CULORI FOLOSITE: ' + str(len(colours_frequencies)) + '\n')
        f.write('NUMAR BUCATI FOLOSITE PE ORIZONTALA: ' + str(columns_count) + '\n')
        f.write('NUMAR BUCATI FOLOSITE PE VERTICALA: ' + str(lines_count) + '\n')
        f.write('NUMAR TOTAL BUCATI FOLOSITE: ' + str(lines_count * columns_count) + '\n')
        f.write('FRECVENTE CULORI: [ID_CULOARE_RAL: NUMAR DE PIESE]\n')
        for code in colours_frequencies:
            pieces_suffix = 'PIESE'
            if colours_frequencies[code] == 1:
                pieces_suffix = 'PIESA'
            f.write('>> ' + code + ': ' + str(colours_frequencies[code]) + ' ' + pieces_suffix + '\n')

    # Crop grid image into A4-sized images (size 29.7 cm x 21.0 cm) and save them to tempdata
    a4_sheets_lines_count = lines_count // 9
    a4_sheets_columns_count = columns_count // 7
    sheet_counter = 1

    for line in range(a4_sheets_lines_count):
        for column in range(a4_sheets_columns_count):
            a4_image = grid_image[line * resolution * upscaling_factor * 9 : (line + 1) * resolution * upscaling_factor * 9,
                                  column * resolution * upscaling_factor * 7 : (column + 1) * resolution * upscaling_factor * 7]
            cv2.imwrite(os.path.join(tempdata_path, 'sheet_' + str(sheet_counter) + '.jpg'), a4_image)
            sheet_counter += 1

    # Separately save the remaining tiles, if any, on the horizontal and vertical
    end_of_horizontal_sheets = a4_sheets_columns_count * resolution * upscaling_factor * 7
    end_of_vertical_sheets = a4_sheets_lines_count * resolution * upscaling_factor * 9
    horizontal_rest_counter = 1
    vertical_rest_counter = 1

    if end_of_horizontal_sheets != grid_image.shape[1]:
        for line in range(a4_sheets_lines_count):
            rest = grid_image[line * resolution * upscaling_factor * 9 : (line + 1) * resolution * upscaling_factor * 9,
                              end_of_horizontal_sheets : ]
            a4_image = np.zeros((resolution * upscaling_factor * 9, resolution * upscaling_factor * 7, channels_count))
            a4_image[:, : rest.shape[1]] = rest

            cv2.imwrite(os.path.join(tempdata_path, 'rest_horizontal_' + str(horizontal_rest_counter) + '.jpg'), a4_image)
            horizontal_rest_counter += 1

    if end_of_vertical_sheets != grid_image.shape[0]:
        for column in range(a4_sheets_columns_count):
            rest = grid_image[end_of_vertical_sheets : ,
                              column * resolution * upscaling_factor * 7 : (column + 1) * resolution * upscaling_factor * 7]
            a4_image = np.zeros((resolution * upscaling_factor * 9, resolution * upscaling_factor * 7, channels_count))
            a4_image[: rest.shape[0], :] = rest

            cv2.imwrite(os.path.join(tempdata_path, 'rest_vertical_' + str(vertical_rest_counter) + '.jpg'), a4_image)
            vertical_rest_counter += 1

    # TODO - If image has rests on both axes, than the intersection of the rests will be left out

    return [pixelated_image, grid_image]
