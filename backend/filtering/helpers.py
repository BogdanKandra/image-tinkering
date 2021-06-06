'''
Created on Sat Nov 30 11:12:39 2019

@author: Bogdan
'''
import os
import sys
import numpy as np
from scipy.signal import convolve2d
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def apply_kernel(image, kernel):
    ''' Performs convolution between the given image and kernel '''
    if utils.is_color(image):
        result_b = convolve2d(image[:,:,0], kernel, mode='same')
        result_g = convolve2d(image[:,:,1], kernel, mode='same')
        result_r = convolve2d(image[:,:,2], kernel, mode='same')
        channels_list = []

        # Trim values lower than 0 or higher than 255 and convert to uint8 for openCV compatibility
        for channel in 'bgr':
            underflow_mask = locals()['result_' + channel] < 0
            result_temp = np.where(underflow_mask, 0, locals()['result_' + channel])
            result_temp = np.where(result_temp > 255, 255, result_temp)
            result_temp = result_temp.astype(np.uint8)
            channels_list.append(result_temp)

        filtered_image = utils.merge_channels(channels_list)
    else:
        # Trim values lower than 0 or higher than 255 and convert to uint8 for openCV compatibility
        filtered_image = convolve2d(image, kernel, mode='same')
        filtered_image = np.where(filtered_image < 0, 0, filtered_image)
        filtered_image = np.where(filtered_image > 255, 255, filtered_image)
        filtered_image = filtered_image.astype(np.uint8)

    return filtered_image

def generate_box_kernel(size):
    ''' Generates a kernel having the given size and giving equal weights to all
    elements surrounding the current pixel '''
    return (1 / size ** 2) * np.ones((size, size), dtype=np.uint8)

def generate_gaussian_kernel(size, sigma=3):
    ''' Generates an one-sum kernel having the given size, containing samples
    from a gaussian distribution having the given standard deviation '''
    size = size // 2
    x, y = np.mgrid[-size : size + 1, -size : size + 1]
    normalization_factor = 1 / (2.0 * np.pi * sigma**2)
    g = np.exp(-((x ** 2 + y ** 2) / (2.0 * sigma ** 2))) * normalization_factor
    g = g / (np.sum(g))    # Normalize the kernel so the sum of elements is 1

    return g

def get_thresholds(image, method, kernel_size):
    ''' Performs convolution between the image and the kernel of the specified
    size. The resulting values are the thresholds used in binarization '''
    if method == 'mean':
        kernel = generate_box_kernel(kernel_size)
    else:
        kernel = generate_gaussian_kernel(kernel_size)

    thresholds = apply_kernel(image, kernel)

    return thresholds

def generate_emboss_kernels(size, direction, type):
    ''' Generates the kernels of the specified type (mask or filter), size and
    direction, needed for the embossing operation '''
    kernel1 = np.zeros((size, size), dtype=np.int8)

    if direction == 'horizontal':
        kernel1[: size // 2, size // 2] = 1
        kernel1[size // 2 + 1 :, size // 2] = -1
        if type == 'filter':
            kernel1[size // 2, size // 2] = 1

        kernel2 = np.flipud(kernel1)
    elif direction == 'vertical':
        kernel1[size // 2, : size // 2] = 1
        kernel1[size // 2, size // 2 + 1 :] = -1
        if type == 'filter':
            kernel1[size // 2, size // 2] = 1

        kernel2 = np.fliplr(kernel1)
    elif direction == 'diagonal':
        for i in range(size):
            if i < size // 2:
                kernel1[i, i] = 1
            elif i > size // 2:
                kernel1[i, i] = -1
            elif type == 'filter':
                kernel1[i, i] = 1

        kernel2 = np.flipud(kernel1)

    return kernel1, kernel2
