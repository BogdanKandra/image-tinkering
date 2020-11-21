'''
Created on Sun Mar 10 15:12:37 2019

@author: Bogdan
'''
import copy
import os
import pickle
import cv2
from matplotlib import pyplot as plt
import numpy as np


def is_grayscale(image):
    ''' Takes an image as parameter and decides whether the image is grayscale
    or not '''
    return len(image.shape) == 2

def is_color(image):
    ''' Takes an image as parameter and decides whether the image is color or
    not '''
    return len(image.shape) != 2

def get_channels(image):
    ''' Takes an image as parameter and returns a list containing its R, G, B (, A)
    channels or the image itself, if it is grayscale '''
    return [copy.deepcopy(image)] if is_grayscale(image) else cv2.split(image)

def merge_channels(channels):
    ''' Takes a list of channels as input and outputs the image obtained by
    merging the channels '''
    return channels[0] if len(channels) == 1 else cv2.merge(tuple(channels))

def get_FFTs(image):
    ''' Takes an image as parameter and returns a list containing the Fast
    Fourier Transforms of each of the image's channels '''
    return [np.fft.fftshift(np.fft.fft2(channel)) for channel in get_channels(image)]

def fft_plot(image, cmap=None):
    ''' Takes a frequency domain image and displays its spectrum

    Arguments:
        image (numPy array) -- the image to be displayed

        cmap (str, optional) -- the color map to be used

    Returns:
        Nothing
    '''
    # Take the magnitudes and reduce values by logarithming
    magnitudes = np.log(np.abs(image) + 1)

    plt.figure()

    plt.subplot(121)
    plt.imshow(image, cmap)
    plt.subplot(122)
    plt.imshow(magnitudes, cmap)

    plt.show()

def resize_dimension(image, new_height=0, new_width=0, interpolation_method=cv2.INTER_LINEAR):
    ''' If one of the dimensions is not given, resizes an image to the specified
    height (or width), while maintaining the original aspect ratio. If given
    both dimensions, resizes an image to the fixed, specified dimensions

    Arguments:
        image (numPy array) -- the image to be resized

        new_height (int, optional) -- the new height (in pixels) of the resized
        image; the default value is 0, meaning that the image will not be
        resized by height

        new_width (int, optional) -- same as "new_height", except for the width;
        if both these arguments are left as default, the original image will be
        returned
    '''
    image_h, image_w = image.shape[:2]
    aspect_ratio = image_w / image_h

    if new_height < 0 or new_width < 0:
        raise ValueError('"new_height" and "new_width" must be positive integers')

    if new_height == 0 and new_width == 0:
        return image
    elif new_height == 0:
        new_height = int(1 / aspect_ratio * new_width)
    elif new_width == 0:
        new_width = int(aspect_ratio * new_height)

    new_shape = (new_width, new_height)

    return cv2.resize(image, new_shape, interpolation=interpolation_method)

def resize_percentage(image, percentage=0):
    ''' Resizes an image by reducing the dimensions to the given percentage of
    the original

    Arguments:
        image (numPy array) -- the image to be resized

        percentage (int, optional) -- the percentage out of the original image's
        dimensions to resize to; the default value of 0 means that no resizing
        will be done
    '''
    image_h, image_w = image.shape[:2]
    aspect_ratio = image_w / image_h

    if percentage == 0:
        return image
    elif percentage < 0:
        raise ValueError('The "percentage" argument must be a positive integer')
    else:
        new_width = int(percentage / 100 * image_w)
        new_height = int(1 / aspect_ratio * new_width)
        new_shape = (new_width, new_height)

        return cv2.resize(image, new_shape)

def generate_image(width, height, r_value, g_value, b_value, image_name, destination_dir):
    ''' Helper which actually generates and saves an image '''
    image = np.zeros((width, height, 3), dtype=np.uint8)
    image[:, :, 0] = r_value
    image[:, :, 1] = g_value
    image[:, :, 2] = b_value
    cv2.imwrite(os.path.join(destination_dir, image_name), image)

def generate_single_color_images(width, height, destination_dir):
    ''' Generates and saves to disk about 1000 single-color rectangle-shaped images '''
    light_values = range(69, 231, 3)
    medium_values = range(46, 154, 2)
    dark_values = range(23, 78, 1)
    index = 1

    # Generate light coloured images
    for value in light_values:
        generate_image(width, height, 69, 230, value, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 69, value, 230, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 230, 69, value, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 230, value, 69, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, value, 69, 230, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, value, 230, 69, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1

    # Generate medium coloured images
    for value in medium_values:
        generate_image(width, height, 46, 153, value, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 46, value, 153, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 153, 46, value, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 153, value, 46, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, value, 46, 153, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, value, 153, 46, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1

    # Generate dark coloured images
    for value in dark_values:
        generate_image(width, height, 23, 77, value, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 23, value, 77, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 77, 23, value, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, 77, value, 23, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, value, 23, 77, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1
        generate_image(width, height, value, 77, 23, 'color_' + str(index) + '.jpg', destination_dir)
        index += 1

def preprocess_image_dataset(input_directory, new_height, new_width, results_prefix, destination_directory):
    ''' Applies several preprocessing operations on the images in the
    input_directory: if present, the alpha channel is stripped; then resizing
    to the given dimensions is performed; finally, the resulting pixel values
    are normalized in the [0, 255] interval '''
    files = os.listdir(input_directory)
    count = 1

    for file in files:
        image = cv2.imread(os.path.join(input_directory, file), cv2.IMREAD_UNCHANGED)
        if image.shape[2] == 4:
            image = image[:, :, :3]
        resized = resize_dimension(image, new_height, new_width, cv2.INTER_AREA)
        normalized = ((resized - np.min(resized)) / (np.max(resized) - np.min(resized)) * 255).astype(np.uint8)

        image_name = results_prefix + '_' + str(count) + '.' + file.split('.')[-1]
        cv2.imwrite(os.path.join(destination_directory, image_name), normalized)
        count += 1

def pickle_imageset_information(input_directory):
    ''' Reads all images present in the input directory; computes, for each
    image, the average values of the red, green and blue channels respectively
    and places them in a dictionary; this dataset's images dimensions and the
    dictionary are serialized in a pickle having the same name as the input directory '''
    files = os.listdir(input_directory)
    averages = {}

    for file in files:
        image = cv2.imread(os.path.join(input_directory, file), cv2.IMREAD_UNCHANGED)
        means = (int(np.mean(image[:,:,0])), int(np.mean(image[:,:,1])), int(np.mean(image[:,:,2])))
        averages[file] = means

    with open(input_directory + '.pickle', 'wb') as p:
        pickle.dump(image.shape[:2], p)
        pickle.dump(averages, p)
