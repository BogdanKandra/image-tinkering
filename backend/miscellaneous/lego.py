"""
Created on Wed Oct 30 16:57:19 2019

@author: Bogdan
"""
import copy
import json
import os
import pickle
import sys
import cv2
import numpy as np
from numpy.lib.recfunctions import structured_to_unstructured, unstructured_to_structured
from PIL import Image, ImageFont, ImageDraw
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend.filtering.spatial import grayscale
from backend import utils


def get_closest_usable_tile_index(distances, tile_usage_grid, line, column):
    """ Helper function which returns the index of the closest tile which has
    not been used on a square centered on the current position, of radius 1 """
    grid_height, grid_width = tile_usage_grid.shape

    while True:
        closest_tile_index = np.argwhere(distances == np.min(distances))[0][-1]
        found = True

        for i in range(line - 1, line + 1):
            for j in range(column - 1, column + 2):
                if 0 <= i < grid_height and 0 <= j < grid_width and \
                        (i != line or j < column) and \
                        tile_usage_grid[i][j] == closest_tile_index:
                    found = False
                    break
            if not found:
                distances = np.delete(distances, np.argwhere(distances == np.min(distances)))
                break

        if found:
            return closest_tile_index


def get_closest_ral_colour(rgb_list):
    """ Function takes a standard RGB colour as argument, computes the closest
    RAL space colour and returns its code and value """
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


def build_mosaic(image, texture, technique, alpha, resolution, redundancy):
    """ Helper function which actually builds the mosaic """
    if utils.is_grayscale(image):
        image = utils.merge_channels([image, image, image])
    else:
        image = image[:, :, :3]

    # Load the appropriate image library information
    database_path = os.path.join(project_path, 'backend', 'miscellaneous', 'database')
    pickle_name = texture + '_' + resolution + '.pickle'
    pickle_path = os.path.join(database_path, pickle_name)

    with open(pickle_path, 'rb') as p:
        tiles_height, tiles_width = pickle.load(p)
        tiles_averages_dict = pickle.load(p)

    # Initialise necessary variables
    tiles_averages = np.zeros((len(tiles_averages_dict), 3))
    tiles_averages_values = list(tiles_averages_dict.values())
    tiles_averages_keys = list(tiles_averages_dict.keys())
    for i in range(len(tiles_averages_dict)):
        tiles_averages[i] = np.array(tiles_averages_values[i])

    image_height, image_width = image.shape[:2]

    mosaic_lines = int(image_height / tiles_height)
    mosaic_columns = int(image_width / tiles_width)
    mosaic_image = np.zeros((mosaic_lines * tiles_height, mosaic_columns * tiles_width, 3), dtype=np.uint8)
    tile_usage_grid = np.ones((mosaic_lines, mosaic_columns), dtype=np.uint8) * -1

    # For each block:
    #    Compute the average r, g, b values of the block and put them in a vector
    #    Compute the distances between the avg vector of the block and each of the avg vectors of the tiles
    #    Replace the current block with the tile located at the shortest distance from the block
    block_averages = np.zeros((1, 3))
    for line in range(mosaic_lines):
        for column in range(mosaic_columns):
            block = image[line * tiles_height: (line + 1) * tiles_height,
                          column * tiles_width: (column + 1) * tiles_width]
            block_averages[0] = np.array((np.mean(block[:, :, 0]), np.mean(block[:, :, 1]), np.mean(block[:, :, 2])))
            distances = cdist(block_averages, tiles_averages)

            # Determine the index of the closest compatible tile
            if redundancy:
                closest_tile_index = np.where(distances == np.min(distances))[1][0]
            else:
                closest_tile_index = get_closest_usable_tile_index(distances, tile_usage_grid, line, column)

            closest_tile_name = tiles_averages_keys[closest_tile_index]
            closest_tile_path = os.path.join(database_path, texture + '_' + resolution, closest_tile_name)
            closest_tile = cv2.imread(closest_tile_path, cv2.IMREAD_UNCHANGED)
            mosaic_image[line * tiles_height: (line + 1) * tiles_height,
                         column * tiles_width: (column + 1) * tiles_width] = closest_tile
            tile_usage_grid[line][column] = closest_tile_index

    if technique == 'alternative':
        # Overlay the mosaic on the input image
        image_copy = utils.resize_dimension(image, *mosaic_image.shape[:2])
        mosaic_image = image_copy * (1 - alpha) + mosaic_image * alpha

    return mosaic_image


def _generate_grid_and_legend(image):
    tile_size = 20  # Controls the size of a grid tile
    symbols = [u'\u25A0', u'\u25A1', u'\u25B2', u'\u25B3', u'\u25B6', u'\u25B7', u'\u1401', u'\u25C6',
               u'\u25C7', u'\u25CF', u'\u25CB', u'\u2605', u'\u2606', u'\u262E', u'\u262F', u'\u2660',
               u'\u2663', u'\u2665', u'\u229E', u'\u22A0', u'\u2A01', u'\u2A02', u'\u2212', u'\u2223',
               u'\u2215', u'\u002B', u'\u003E', u'\u003D', u'\u0023', u'\u0024', u'\u20A4', u'\u20AC',
               u'\u0025', u'\u0026', u'\u2217', u'\u0040', u'\u2200', u'\u2203', u'\u2211', u'\u220F',
               u'\u03A8', u'\u03A9', u'\u00A4', u'\u03DE', u'\u1455', u'\u22C0', u'\u222B', u'\u22C8',
               u'\u25D0', u'\u25D1', u'\u25D2', u'\u25D3', u'\u25D4', u'\u25D5', u'\u25D6', u'\u25D7',
               u'\u265A', u'\u265B', u'\u265C', u'\u265D', u'\u265E', u'\u265F', u'\u2690', u'\u2691']

    image_height, image_width = image.shape[:2]
    grid_image = np.full((tile_size * image_height,
                          tile_size * image_width), fill_value=255, dtype=np.uint8)
    grid_tile = np.empty((tile_size, tile_size), dtype=np.uint8)

    # Configure the text to be used for writing the template grid
    font_path = os.path.join(project_path, 'webui', 'static', 'fonts', 'DejaVuSans.ttf')
    font = ImageFont.truetype(font_path, 14)

    # Create correspondence between the image colours and symbols used in the grid
    image_colours = np.unique(image.reshape((-1, 3)), axis=0)
    colours_to_symbols = {}

    for index, colour in enumerate(image_colours):
        colours_to_symbols[tuple(colour)] = symbols[index]

    # For each pixel of the quantized image, generate a tile in the grid image
    for i in range(image_height):
        for j in range(image_width):
            # Set a 1-pixel black border around the grid tile
            grid_tile[:, :] = 255
            grid_tile[0, :] = 0
            grid_tile[-1, :] = 0
            grid_tile[:, 0] = 0
            grid_tile[:, -1] = 0

            # Write the symbol in the center of the tile
            symbol = colours_to_symbols[tuple(image[i, j, :])]
            grid_tile_pil = Image.fromarray(grid_tile)
            drawer = ImageDraw.Draw(grid_tile_pil)
            text_size = drawer.textsize(symbol, font=font)
            text_x = (tile_size - text_size[0]) // 2 + 1
            text_y = (tile_size - text_size[1]) // 2 - 1
            drawer.text((text_x, text_y), text=symbol, fill=0, font=font)

            # Store the tile in the grid
            grid_tile = np.array(grid_tile_pil)
            grid_image[i * tile_size: (i + 1) * tile_size,
                       j * tile_size: (j + 1) * tile_size] = grid_tile

    # Split the grid image into subimages for printing
    tempdata_path = os.path.join(project_path, 'webui', 'static', 'tempdata')
    grid_height, grid_width = grid_image.shape[:2]
    sheet_counter = 1
    subimages_dict = {}

    # Decide how the grid image will be split
    if image_height > image_width:  # Split into 3 x 2
        subimages_width = 2
        subimages_height = 3
    elif image_height < image_width:  # Split into 2 x 3
        subimages_width = 3
        subimages_height = 2
    else:  # Split into 3 x 3
        subimages_width = 3
        subimages_height = 3

    # Set the step as the closest multiple of the tile size * 10, so the subimages will finish at multiples of 10
    step_x = round((grid_width // subimages_width // tile_size) / 10) * tile_size * 10
    step_y = round((grid_height // subimages_height // tile_size) / 10) * tile_size * 10

    for top_index in range(0, grid_height, step_y):
        bottom_index = top_index + step_y

        for left_index in range(0, grid_width, step_x):
            right_index = left_index + step_x

            subimage = grid_image[top_index: bottom_index, left_index: right_index]
            subimages_dict[sheet_counter] = copy.copy(subimage)
            sheet_counter += 1

    # Write line and column counters on the grid subimages
    font = ImageFont.truetype(font_path, 10)
    line_number = 0
    column_number = 0
    sheet_counter = 1

    for _ in range(subimages_height):
        for _ in range(subimages_width):
            subimage = subimages_dict[sheet_counter]
            numbered_subimage = np.full((tile_size + subimage.shape[0],
                                         tile_size + subimage.shape[1]), fill_value=255, dtype=np.uint8)
            numbered_subimage[tile_size:, tile_size:] = subimage

            for i in range(line_number, line_number + (subimage.shape[0] // tile_size), 10):
                # Write the number in the center of the tile
                grid_tile[:, :] = 255
                grid_tile_pil = Image.fromarray(grid_tile)
                drawer = ImageDraw.Draw(grid_tile_pil)
                text_size = drawer.textsize(str(i), font=font)
                text_x = (tile_size - text_size[0]) // 2 + 1
                text_y = (tile_size - text_size[1]) // 2 - 1
                drawer.text((text_x, text_y), text=str(i), fill=0, font=font)

                # Store the tile in the grid
                grid_tile = np.array(grid_tile_pil)
                numbered_subimage[(i - line_number) * tile_size: (i + 1 - line_number) * tile_size,
                                  0: tile_size] = grid_tile

            for j in range(column_number, column_number + (subimage.shape[1] // tile_size), 10):
                # Write the number in the center of the tile
                grid_tile[:, :] = 255
                grid_tile_pil = Image.fromarray(grid_tile)
                drawer = ImageDraw.Draw(grid_tile_pil)
                text_size = drawer.textsize(str(j), font=font)
                text_x = (tile_size - text_size[0]) // 2 + 1
                text_y = (tile_size - text_size[1]) // 2 - 1
                drawer.text((text_x, text_y), text=str(j), fill=0, font=font)

                # Store the tile in the grid
                grid_tile = np.array(grid_tile_pil)
                numbered_subimage[0: tile_size,
                                  (j - column_number) * tile_size: (j + 1 - column_number) * tile_size] = grid_tile

            column_number += subimage.shape[1] // tile_size
            subimages_dict[sheet_counter] = copy.copy(numbered_subimage)
            cv2.imwrite(os.path.join(tempdata_path, 'sheet_' + str(sheet_counter) + '.jpg'), numbered_subimage)
            sheet_counter += 1

        line_number += subimage.shape[0] // tile_size
        column_number = 0

    # Generate image containing sheet numbering and colours to symbols
    # The image will be 1485 x 1050 pixels, a multiple of A4 format
    legend_image = np.full((1485, 1050, 3), fill_value=255, dtype=np.uint8)
    diagram_tile = np.full((80, 60, 3), fill_value=255, dtype=np.uint8)
    colour_tile = np.full((30, 200, 3), fill_value=255, dtype=np.uint8)
    symbol_tile = np.full((30, 30, 3), fill_value=255, dtype=np.uint8)
    sheet_counter = 1
    font = ImageFont.truetype(font_path, 14)

    # Write the cross-stitch diagram
    legend_image_pil = Image.fromarray(legend_image)
    drawer = ImageDraw.Draw(legend_image_pil)
    drawer.text((30, 30), text='DIAGRAMĂ GOBLEN', fill=0, font=font)
    legend_image = np.array(legend_image_pil)

    for i in range(subimages_height):
        for j in range(subimages_width):
            diagram_tile[:, :, :] = 255
            diagram_tile[0, :, :] = 0
            diagram_tile[-1, :, :] = 0
            diagram_tile[:, 0, :] = 0
            diagram_tile[:, -1, :] = 0

            diagram_tile_pil = Image.fromarray(diagram_tile)
            drawer = ImageDraw.Draw(diagram_tile_pil)
            drawer.text((10, 10), text=str(sheet_counter), fill=0, font=font)
            diagram_tile = np.array(diagram_tile_pil)

            legend_image[50 + i * diagram_tile.shape[0]: 50 + (i + 1) * diagram_tile.shape[0],
                         30 + j * diagram_tile.shape[1]: 30 + (j + 1) * diagram_tile.shape[1]] = diagram_tile

            sheet_counter += 1

    # Write the colours-to-symbols legend
    vertical_index = 100 + subimages_height * diagram_tile.shape[0]
    legend_image_pil = Image.fromarray(legend_image)
    drawer = ImageDraw.Draw(legend_image_pil)
    drawer.text((30, vertical_index), text='LEGENDĂ CULORI', fill=0, font=font)
    legend_image = np.array(legend_image_pil)

    entry_index = 1
    vertical_index = 100 + subimages_height * diagram_tile.shape[0]
    font = ImageFont.truetype(font_path, 18)

    for colour, symbol in colours_to_symbols.items():
        colour_tile[:, :, :] = colour
        colour_tile[0, :, :] = 0
        colour_tile[-1, :, :] = 0
        colour_tile[:, 0, :] = 0
        colour_tile[:, -1, :] = 0

        symbol_tile[:, :, :] = 255
        symbol_tile[0, :, :] = 0
        symbol_tile[-1, :, :] = 0
        symbol_tile[:, 0, :] = 0
        symbol_tile[:, -1, :] = 0

        symbol_tile_pil = Image.fromarray(symbol_tile)
        drawer = ImageDraw.Draw(symbol_tile_pil)
        text_size = drawer.textsize(symbol, font=font)
        text_x = (symbol_tile.shape[0] - text_size[0]) // 2
        text_y = (symbol_tile.shape[1] - text_size[1]) // 2 - 2
        drawer.text((text_x, text_y), text=symbol, fill=0, font=font)
        symbol_tile = np.array(symbol_tile_pil)

        legend_image[vertical_index + entry_index * symbol_tile.shape[0]:
                     vertical_index + (entry_index + 1) * symbol_tile.shape[0],
                     30: 30 + symbol_tile.shape[1]] = symbol_tile
        legend_image[vertical_index + entry_index * symbol_tile.shape[0]:
                     vertical_index + (entry_index + 1) * symbol_tile.shape[0],
                     40 + symbol_tile.shape[1]: 40 + symbol_tile.shape[1] + colour_tile.shape[1]] = colour_tile

        entry_index += 1
        vertical_index += 10

    return grid_image, legend_image


def _median_cut(image, colours):
    """ An improved version of the Median Cut quantization algorithm """
    if utils.is_color(image):
        # Remove the alpha channel, if present
        if image.shape[2] == 4:
            image = image[:, :, :3]

        # Determine the channel having the greatest range
        range_b = np.amax(image[:, :, 0]) - np.amin(image[:, :, 0])
        range_g = np.amax(image[:, :, 1]) - np.amin(image[:, :, 1])
        range_r = np.amax(image[:, :, 2]) - np.amin(image[:, :, 2])
        greatest_range_index = np.argmax([range_b, range_g, range_r])

        # Sort the image pixels according to that channel's values
        pixels = np.reshape(image, (-1, 3))
        pixels = unstructured_to_structured(pixels, np.dtype([('b', int), ('g', int), ('r', int)]))
        sorting_indices = np.argsort(pixels, order='bgr'[greatest_range_index])
        pixels_sorted = pixels[sorting_indices]

        # Split the pixels list into <colours> buckets and compute the average of each bucket
        buckets = np.array_split(pixels_sorted, colours)
        bucket_averages = [(int(np.average(bucket['b'])),
                            int(np.average(bucket['g'])),
                            int(np.average(bucket['r']))) for bucket in buckets]

        # Assign the averages to the pixels contained in the buckets
        left_index = 0
        right_index = len(buckets[0])
        for i in range(len(buckets)):
            pixels_sorted[left_index: right_index] = bucket_averages[i]
            left_index = right_index
            if i + 1 < len(buckets):
                right_index += len(buckets[i + 1])

        # Return the quantized image
        pixels_sorted = structured_to_unstructured(pixels_sorted)
        pixels = pixels_sorted[np.argsort(sorting_indices)]
        quantized_image = np.reshape(pixels, image.shape)
    else:
        # Sort the image pixels
        pixels = np.ravel(image)
        sorting_indices = np.argsort(pixels)
        pixels_sorted = pixels[sorting_indices]

        # Split the pixels list into <colours> buckets and compute the average of each bucket
        buckets = np.array_split(pixels_sorted, colours)
        bucket_averages = [int(np.average(bucket)) for bucket in buckets]

        # Assign the averages to the pixels contained in the buckets
        left_index = 0
        right_index = len(buckets[0])
        for i in range(len(buckets)):
            pixels_sorted[left_index: right_index] = bucket_averages[i]
            left_index = right_index
            if i + 1 < len(buckets):
                right_index += len(buckets[i + 1])

        # Return the quantized image
        pixels = pixels_sorted[np.argsort(sorting_indices)]
        quantized_image = np.reshape(pixels, image.shape)

    return quantized_image


def _k_means(image, colours):
    """ K-Means clustering applied to an image """
    if utils.is_color(image):
        # Remove the alpha channel, if present
        if image.shape[2] == 4:
            image = image[:, :, :3]

        pixels = np.reshape(image, (-1, image.shape[2]))
    else:
        pixels = np.reshape(image, (image.shape[0] * image.shape[1]))

    sample_count = int(0.01 * len(pixels))
    pixels_sample = shuffle(pixels, n_samples=sample_count)
    kmeans_estimator = KMeans(n_clusters=colours).fit(pixels_sample)
    labels = kmeans_estimator.predict(pixels)
    centers = kmeans_estimator.cluster_centers_
    pixels = centers[labels].astype(np.uint8)
    quantized_image = np.reshape(pixels, image.shape)

    return quantized_image


def ascii_art(image, extra_inputs, parameters):
    """ Applies an **ASCII Art Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs
        for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *charset* (str, optional) -- the character set to use when
            rendering ASCII art image; possible values are *standard*,
            *alternate* and *full*; default value is *alternate*

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    """
    # Small, 11 character ramps
    STANDARD_CHARSET = [' ', '.', ',', ':', '-', '=', '+', '*', '#', '%', '@']
    ALTERNATE_CHARSET = [' ', '.', ',', ':', '-', '=', '+', '*', '%', '@', '#']

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
    CHARS = CHARS[::-1]  # Reverse the list

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
    dy = 14  # Vertical offset to account for the characters height
    ascii_image = np.zeros((number_of_lines * dy, number_of_cols), np.uint8)
    ascii_image[:, :] = 255

    for i, line in enumerate(lines):
        y = i * dy
        for j, char in enumerate(line):
            cv2.putText(ascii_image, char, (j * maximum_letter_width, y),
                        font_face, 1, (0, 0, 0), 1, lineType=cv2.FILLED)

    # Resize resulting image to original size of input image
    ascii_image = cv2.resize(ascii_image, original_size, interpolation=cv2.INTER_AREA)

    return [ascii_image]


def photomosaic(image, extra_inputs, parameters):
    """ Builds a photomosaic which approximates the given image, using the
    database image tiles.

    Arguments:
        *image* (NumPy array) -- the image to be approximated by a photo mosaic

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs
        for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *technique* (str, optional) -- the technique used when building the
            photomosaic; possible values are *original* and *alternative*;
            default value is *original*

            *texture* (str, optional) -- the image database used when building
            the photomosaic; possible values are *cakes* and *cars*; default
            value is *cakes*

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
    """
    # Parameters extraction
    if 'technique' in parameters:
        technique = parameters['technique']
    else:
        technique = 'original'

    if 'texture' in parameters:
        texture = parameters['texture']
    else:
        texture = 'cakes'

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
    alpha = None
    if technique == 'alternative':
        if transparency == 'low':
            alpha = 205 / 255
        elif transparency == 'medium':
            alpha = 150 / 255
        elif transparency == 'high':
            alpha = 75 / 255

    mosaic_image = build_mosaic(image, texture, technique, alpha, resolution, redundancy)

    return [mosaic_image]


def pixelate(image, extra_inputs, parameters):
    """ Uses a form of downscaling in order to achieve an 8-bit-like filter
    appearance of an image.

    Arguments:
        *image* (NumPy array) -- the image to be pixelated

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs
        for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *fidelity* (str, optional) -- how close the resulting image will
            look compared to the original (inverse proportional to the size of
            the composing pixels); possible values are *very low*, *low*,
            *standard*, *high*, *very high* and *ultra high*; default value is
            *standard*

    Returns:
        list of NumPy array uint8 -- list containing the pixelated image
    """
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
        pixelated_image = np.zeros((lines_count * resolution,
                                    columns_count * resolution, channels_count), dtype=np.uint8)
    else:
        pixel_tile = np.zeros((resolution, resolution))
        pixelated_image = np.zeros((lines_count * resolution, columns_count * resolution), dtype=np.uint8)

    # For each block:
    #    Compute the average r, g, b values of the block and put them in a vector
    #    Replace the current block with a tile coloured the same as the average vector
    for line in range(lines_count):
        for column in range(columns_count):
            block = image[line * resolution: (line + 1) * resolution, column * resolution: (column + 1) * resolution]
            if utils.is_color(image):
                for i in range(channels_count):
                    colour_component = int(round(np.mean(block[:, :, i])))
                    pixel_tile[:, :, i] = colour_component
            else:
                pixel_tile = int(round(np.mean(block)))

            pixelated_image[line * resolution: (line + 1) * resolution,
                            column * resolution: (column + 1) * resolution] = pixel_tile

    return [pixelated_image]


def quantize(image, extra_inputs, parameters):
    """ Quantizes an image (Reduces the number of colours present in it).

    Arguments:
        *image* (NumPy array) -- the image to be quantized

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *colours* (int, optional) -- the size of the colour palette used in the quantized image;
            default value is 256

            *algorithm* (str, optional) -- the algorithm to be used for quantization; possible values are *median cut*
            and *k-means*; default value is *k-means*

    Returns:
        list of NumPy array uint8 -- list containing the quantized image
    """
    # Parameters extraction
    if 'colours' in parameters:
        colours = parameters['colours']
    else:
        colours = 256

    if 'algorithm' in parameters:
        algorithm = parameters['algorithm']
    else:
        algorithm = 'k-means'

    if algorithm == 'median cut':
        quantized_image = _median_cut(image, colours)
    else:
        quantized_image = _k_means(image, colours)

    return [quantized_image]


def pixelate_ral(image, extra_inputs, parameters):
    """ A modified version of the pixelate operation, used for converting images
    into a version suitable for mosaicing. The colour representation used is a
    subset of RGB called RAL, a standard used for paint colours. In addition, a
    text file containing extra information is created.

    Arguments:
        *image* (NumPy array) -- the image to be pixelated

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs
        for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the pixelated image
    """
    # Initialisations; constants are measured in centimeters
    tile_size = 3
    mosaic_width = 190
    mosaic_height = 250
    mosaic_lines_count = mosaic_height // tile_size
    mosaic_columns_count = mosaic_width // tile_size

    # Compute how many pixels will each block contain
    image_height, image_width = image.shape[:2]
    block_width = image_width // mosaic_columns_count
    block_height = image_height // mosaic_lines_count

    # Configure the text to be used for writing the template grid
    font_face = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 0.6
    thickness = 1
    upscaling_factor = 6

    if utils.is_color(image):
        channels_count = image.shape[2]
        pixel_tile = np.zeros((block_height * upscaling_factor, block_width * upscaling_factor, channels_count))
        grid_tile = np.zeros((block_height * upscaling_factor, block_width * upscaling_factor, channels_count))
        pixelated_image = np.zeros((image_height * upscaling_factor,
                                    image_width * upscaling_factor, channels_count), dtype=np.uint8)
        grid_image = np.zeros((image_height * upscaling_factor,
                               image_width * upscaling_factor, channels_count), dtype=np.uint8)
        colours_frequencies = {}
    else:
        pixel_tile = np.zeros((block_height * upscaling_factor, block_width * upscaling_factor))
        grid_tile = np.zeros((block_height * upscaling_factor, block_width * upscaling_factor))
        pixelated_image = np.zeros((image_height * upscaling_factor,
                                    image_width * upscaling_factor), dtype=np.uint8)
        grid_image = np.zeros((image_height * upscaling_factor,
                               image_width * upscaling_factor), dtype=np.uint8)

    # For each block:
    #    Compute the average r, g, b values of the block and put them in a vector
    #    Replace the current block with a tile coloured as the closest RAL colour
    #    in relation to the average vector
    for line in range(mosaic_lines_count):
        for column in range(mosaic_columns_count):
            block = image[line * block_height: (line + 1) * block_height,
                          column * block_width: (column + 1) * block_width]
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
                text_x = (block_width * upscaling_factor - text_size[0]) // 2
                text_y = (block_height * upscaling_factor + text_size[1]) // 2
                cv2.putText(grid_tile, ral_code, (text_x, text_y), font_face, font_scale, (0, 0, 0), thickness)
            else:
                pixel_tile = int(round(np.mean(block)))

            pixelated_image[line * block_height * upscaling_factor: (line + 1) * block_height * upscaling_factor,
                            column * block_width * upscaling_factor: (column + 1) * block_width * upscaling_factor] = pixel_tile
            grid_image[line * block_height * upscaling_factor: (line + 1) * block_height * upscaling_factor,
                       column * block_width * upscaling_factor: (column + 1) * block_width * upscaling_factor] = grid_tile

    # Write colour usage information into a file
    tempdata_path = os.path.join(project_path, 'webui', 'static', 'tempdata')
    with open(os.path.join(tempdata_path, 'ral_info.txt'), 'w') as f:
        f.write('INFORMATII MOZAIC:\n')
        f.write('==============================\n')
        f.write('NUMAR CULORI: ' + str(len(colours_frequencies)) + '\n')
        f.write('NUMAR BUCATI PE ORIZONTALA: ' + str(mosaic_columns_count) + '\n')
        f.write('NUMAR BUCATI PE VERTICALA: ' + str(mosaic_lines_count) + '\n')
        f.write('NUMAR TOTAL BUCATI: ' + str(mosaic_lines_count * mosaic_columns_count) + '\n')
        f.write('FRECVENTE CULORI: [ID_CULOARE_RAL: NUMAR DE PIESE]\n')
        for code in colours_frequencies:
            pieces_suffix = 'PIESE'
            if colours_frequencies[code] == 1:
                pieces_suffix = 'PIESA'
            f.write('>> ' + code + ': ' + str(colours_frequencies[code]) + ' ' + pieces_suffix + '\n')

    # Crop grid image into A4-sized images (size 29.7 cm x 21.0 cm) and save them to tempdata
    a4_sheets_lines_count = mosaic_lines_count // 9
    a4_sheets_columns_count = mosaic_columns_count // 7
    sheet_counter = 1

    for line in range(a4_sheets_lines_count):
        for column in range(a4_sheets_columns_count):
            a4_image = grid_image[
                       line * block_height * upscaling_factor * 9: (line + 1) * block_height * upscaling_factor * 9,
                       column * block_width * upscaling_factor * 7: (column + 1) * block_width * upscaling_factor * 7]
            cv2.imwrite(os.path.join(tempdata_path, 'sheet_' + str(sheet_counter) + '.jpg'), a4_image)
            sheet_counter += 1

    # Separately save the remaining tiles, if any, on the horizontal and vertical
    end_of_horizontal_sheets = a4_sheets_columns_count * block_width * upscaling_factor * 7
    end_of_vertical_sheets = a4_sheets_lines_count * block_height * upscaling_factor * 9
    horizontal_rest_counter = 1
    vertical_rest_counter = 1

    if end_of_horizontal_sheets != grid_image.shape[1]:
        for line in range(a4_sheets_lines_count):
            rest = grid_image[
                   line * block_height * upscaling_factor * 9: (line + 1) * block_height * upscaling_factor * 9,
                   end_of_horizontal_sheets:]
            a4_image = np.zeros(
                (block_height * upscaling_factor * 9, block_width * upscaling_factor * 7, channels_count))
            a4_image[:, : rest.shape[1]] = rest

            horizontal_rest_path = os.path.join(tempdata_path,
                                                'rest_horizontal_' + str(horizontal_rest_counter) + '.jpg')
            cv2.imwrite(horizontal_rest_path, a4_image)
            horizontal_rest_counter += 1

    if end_of_vertical_sheets != grid_image.shape[0]:
        for column in range(a4_sheets_columns_count):
            rest = grid_image[end_of_vertical_sheets:,
                              column * block_width * upscaling_factor * 7: (column + 1) * block_width * upscaling_factor * 7]
            a4_image = np.zeros(
                (block_height * upscaling_factor * 9, block_width * upscaling_factor * 7, channels_count))
            a4_image[: rest.shape[0], :] = rest

            cv2.imwrite(os.path.join(tempdata_path, 'rest_vertical_' + str(vertical_rest_counter) + '.jpg'), a4_image)
            vertical_rest_counter += 1

    # TODO - If image has rests on both axes, then the intersection of the rests will be left out

    return [pixelated_image, grid_image]


def cross_stitch(image, extra_inputs, parameters):
    """ Performs color quantization in the input image and generates a template used for cross-stitching.

    Arguments:
        *image* (NumPy array) -- the image to be pixelated

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *target_Height* (int) -- the maximum number of points that the cross-stitch will have on each column

            *target_Width* (int) -- the maximum number of points that the cross-stitch will have on each line

            *colours* (int, optional) -- the number of colours that the cross-stitch will contain; default value is 20

    Returns:
        list of NumPy array uint8 -- list containing the quantized image and the cross-stitch template
    """
    # Parameters extraction
    target_height = parameters['target_Height']
    target_width = parameters['target_Width']

    if 'colours' in parameters:
        colours = parameters['colours']
    else:
        colours = 20

    # Resize the input image, keeping its original aspect ratio
    height, width = image.shape[:2]
    resizing_constant = max(height / target_height, width / target_width)
    resized_height = int(height / resizing_constant)
    resized_width = int(width / resizing_constant)
    resized_image = utils.resize_dimension(image, resized_height, resized_width)

    # Quantize the resized image
    quantized_image = quantize(resized_image, {}, {'colours': colours})[0]

    # Generate the cross-stitch template and legent
    grid_image, legend_image = _generate_grid_and_legend(quantized_image)

    return [quantized_image, grid_image, legend_image]
