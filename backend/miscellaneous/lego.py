"""
Created on Wed Oct 30 16:57:19 2019

@author: Bogdan
"""
import os
import sys
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def mosaicing(image, extra_inputs, parameters):
    ''' Builds a photomosaic which approximates the given image, using the database image tiles.

    Arguments:
        *image* (NumPy array) -- the image to be approximated by a photo mosaic

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary holding parameter values (empty)

    Returns:
        list of NumPy array uint8 -- list containing the photomosaic of the image
    '''

def collage_maker():
    ''' Google "photo collage maker" '''
    pass
