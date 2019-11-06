"""
Created on Wed Oct 30 16:57:19 2019

@author: Bogdan
"""
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
from backend import utils


def get_closest_usable_tile_index(distances, tile_usage_grid, line, column):
    ''' Helper function which returns the index of the closest tile which has not been used on a
    square centered on the current position, of radius 1 '''
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

def build_mosaic(image, technique, texture, alpha_level, resolution, redundancy):
    ''' Helper function which actually builds the mosaic '''
    pickle_name = texture + '_' + resolution + '.pickle'
    database_path = os.path.join(project_path, 'backend', 'miscellaneous', 'database')
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
            closest_tile = cv2.imread(os.path.join(database_path, texture + '_' + resolution, closest_tile_name), cv2.IMREAD_UNCHANGED)
            mosaic_image[line * tiles_height : (line + 1) * tiles_height, column * tiles_width : (column + 1) * tiles_width] = closest_tile
            tile_usage_grid[line][column] = closest_tile_index

    if technique == 'alternative':
        # Overlay the mosaic on the input image
        image_copy = utils.resize_dimension(image, *mosaic_image.shape[:2])
        mosaic_image = image_copy * (1 - alpha_level) + mosaic_image * alpha_level

    return mosaic_image

def photomosaic(image, extra_inputs, parameters):
    ''' Builds a photomosaic which approximates the given image, using the database image tiles.

    Arguments:
        *image* (NumPy array) -- the image to be approximated by a photo mosaic

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *technique* (str, optional) -- the technique used when building the photomosaic;
            possible values are *original* and *alternative*; default value is *original*

            *texture* (str) -- the texture used to build the photo mosaic; possible values are
            *cakes* and *pixels*; the *pixels* texture is only compatible with *original* technique

            *transparency* (str, optional) -- the level of transparency of the mosaic image;
            possible values are *high*, *medium* and *low*; this parameter is ignored unless
            *technique* == *alternative*; default value is *high*

            *resolution* (str, optional) -- the resolution of the photomosaic; possible values are
            *low*, *standard* and *high*; default value is *standard*
            
            *redundancy* (str, optional) -- whether or not to allow the same tile to be repeated for
            neighbours; possible values are *allowed* and *not allowed*; default value is *allowed*

    Returns:
        list of NumPy array uint8 -- list containing the photomosaic of the image
    '''
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

    # Determine the pickle to be loaded based on requested texture and resolution
    if texture == 'pixels':
        if resolution == 'low':
            resolution = '20x20'
        elif resolution == 'standard':
            resolution = '10x10'
        elif resolution == 'high':
            resolution = '5x5'
    elif texture == 'cakes':
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

    mosaic_image = build_mosaic(image, technique, texture, alpha_level, resolution, redundancy)

    return [mosaic_image]

def collage_maker():
    ''' Google "photo collage maker" '''
    pass
