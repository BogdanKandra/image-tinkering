'''
Created on Sat May 18 16:58:05 2019

@author: Bogdan
'''
import os
import sys
import cv2
import numpy as np
from . import helpers
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


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

def binarize(image, extra_inputs={}, parameters={}):
    ''' Binarizes an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be binarized

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *thresholding_Method* (str, optional) -- the type of thresholding; possible values are
            *simple* and *adaptive*; default value is *adaptive*. In the case of *simple*
            thresholding, the binarization threshold is chosen by the user and it is the same for
            all pixels; this can cause unsatisfactory results if the source image has different
            lighting conditions in different areas. In *adaptive* thresholding, the threshold is
            automatically computed and is different for each source pixel

            *threshold* (str, optional) -- the value which separates the two pixel values, in the
            case of simple thresholding; possible values are *median* and *127*; default value is
            *median*

            *maximum_Value* (int, optional) -- the value with which to replace pixel values greater
            than the threshold; default value is 255; must be between 1 and 255

            *adaptive_Method* (str, optional) -- the type of adaptive threshold computation;
            possible values are *mean* and *gaussian*; default value is *gaussian*. When *mean*,
            the threshold is computed as the mean of the values in the neighbourhood; when
            *gaussian*, the threshold is computed as a gaussian-weighted sum of the neighbourhood
            values

            *neighbourhood_Size* (int, optional) -- the square size of the neighbourhood of values
            to consider when computing adaptive thresholds; possible values are *5*, *9* and *15*;
            default value is 15
    '''
    if utils.is_color(image):
        image = grayscale(image, {}, {})[0]

    if 'thresholding_Method' in parameters:
        thresholding = parameters['thresholding_Method']
    else:
        thresholding = 'adaptive'

    if 'maximum_Value' in parameters:
        max_value = parameters['maximum_Value']
    else:
        max_value = 255

    if thresholding == 'simple':
        threshold = parameters['threshold']

        if threshold == 'median':
            threshold = np.median(image)
        else:
            threshold = 127

        # If the pixel value is greater than the threshold, set the pixel value to 'max_value'
        # Otherwise, set it to 0
        binary_image = np.where(image > threshold, max_value, 0).astype(np.uint8)
    else:
        if 'adaptive_Method' in parameters:
            method = parameters['adaptive_Method']
        else:
            method = 'gaussian'

        if 'neighbourhood_Size' in parameters:
            neighbourhood_size = parameters['neighbourhood_Size']
        else:
            neighbourhood_size = 15

        # Compute the thresholds and set the new values accordingly
        thresholds = helpers.get_thresholds(image, method, neighbourhood_size) - 2
        binary_image = np.where(image > thresholds, max_value, 0).astype(np.uint8)

    return [binary_image]

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
    elif strength == 'strong':
        size = 17

    if 'backend.filtering.helpers' in sys.modules:
        module_key = 'backend.filtering.helpers'
    else:
        module_key = 'filtering.helpers'

    kernel = getattr(sys.modules[module_key], 'generate_{}_kernel'.format(kernel))(size)
    blurred_image = helpers.apply_kernel(image, kernel)

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
    # Adding the details image to the original results in a sharpened image
    blurred_image = blur(image, {}, {'type': kernel, 'strength': strength})[0]
    details_image = np.where(image - blurred_image < 0, 0, image - blurred_image)
    sharpened_image = np.where(image + details_image > 255, 255, image + details_image)

##### Alternative implementation using kernels
#    sharp_3x3_1 = np.array([[0, -1, 0],
#                            [-1, 5, -1],
#                            [0, -1, 0]])
#    sharp_3x3_2 = np.array([[-1, -1, -1],
#                            [-1, 9, -1],
#                            [-1, -1, -1]])
#    sharp_3x3_3 = np.array([[-1/8, -1/8, -1/8],
#                            [-1/8, 2, -1/8],
#                            [-1/8, -1/8, -1/8]])
    # Unsharp masking kernel
#    sharp_5x5 = np.array([[-0.00391, -0.01563, -0.02344, -0.01563, -0.00391],
#                          [-0.01563, -0.06250, -0.09375, -0.06250, -0.01563],
#                          [-0.02344, -0.09375, 1.85980, -0.09375, -0.02344],
#                          [-0.01563, -0.06250, -0.09375, -0.06250, -0.01563],
#                          [-0.00391, -0.01563, -0.02344, -0.01563, -0.00391]])
#
#    sharpened_image = apply_kernel(image, sharp_5x5)

    return [sharpened_image]

def edge(image, extra_inputs, parameters):
    '''Performs edge detection onto an image and returns the edge image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *method* (str) -- the type of edge detection algorithm to be applied; possible values
            are *laplacian*, *gradient*, *non-max suppression*, *canny*

            *pre-Blur* (str, optional) -- whether to apply blur to the input image before convolving
            with the laplacian kernel; possible values are 'yes' and 'no'; default value is 'yes'

            *edge_Count* (str, optional) -- how many edges wil be considered strong by the Canny
            Edge Algorithm; possible values are *standard* and *many*; default value is *standard*

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    # Parameters extraction
    method = parameters['method']

    if 'pre-Blur' in parameters:
        pre_blur = parameters['pre-Blur']
        if pre_blur == 'yes':
            pre_blur = True
        else:
            pre_blur = False
    else:
        pre_blur = True

    if 'edge_Count' in parameters:
        count = parameters['edge_Count']
    else:
        count = 'standard'

    if method == 'laplacian':  # The Laplacian operator of the image is computed
        # Preprocess the input image
        if pre_blur:
            gray = grayscale(image, {}, {})[0]
            blur_kernel = helpers.generate_gaussian_kernel(3, 1)
            processed_image = helpers.apply_kernel(gray, blur_kernel)
        else:
            processed_image = grayscale(image, {}, {})[0]

        # Convolve processed image with the laplacian kernel
        laplacian_kernel_alt = np.array([[-1, -1, -1],
                                         [-1, 8, -1],
                                         [-1, -1, -1]])
#       ### Original Laplacian kernel -- gives weaker edges
#                edge_kernel_og = np.array([[0, -1, 0],
#                                           [-1, 4, -1],
#                                           [0, -1, 0]])

        laplacian_image = helpers.apply_kernel(processed_image, laplacian_kernel_alt)

        return [laplacian_image]
    else:  # The Canny Edge Algorithm is implemented
        ### Preprocess the input image -- blurring is necessary so noise is removed
        gray = grayscale(image, {}, {})[0]
        blur_kernel = helpers.generate_gaussian_kernel(3, 1)
        blurred = helpers.apply_kernel(gray, blur_kernel)

        ### Image Gradient computation (Angles and Normalized Magnitudes)
        sobel_x_left = np.array([[-1, 0, 1],
                                 [-2, 0, 2],
                                 [-1, 0, 1]])
        sobel_y_bottom = np.array([[1, 2, 1],
                                   [0, 0, 0],
                                   [-1, -2, -1]])
        sobel_x_right = np.array([[1, 0, -1],
                                  [2, 0, -2],
                                  [1, 0, -1]])
        sobel_y_top = np.array([[-1, -2, -1],
                                [0, 0, 0],
                                [1, 2, 1]])

        derivative_x_left = helpers.apply_kernel(blurred, sobel_x_left)
        derivative_x_right = helpers.apply_kernel(blurred, sobel_x_right)
        derivative_x = derivative_x_left + derivative_x_right

        derivative_y_bottom = helpers.apply_kernel(blurred, sobel_y_bottom)
        derivative_y_top = helpers.apply_kernel(blurred, sobel_y_top)
        derivative_y = derivative_y_bottom + derivative_y_top

        gradient_magnitude = np.hypot(derivative_x, derivative_y)
        gradient_magnitude = gradient_magnitude / gradient_magnitude.max() * 255

        if method == 'gradient':
            return [gradient_magnitude.astype(np.uint8)]

        ### Non-Maximum Suppression step
        height, width = image.shape[:2]

        gradient_radians = np.arctan2(derivative_y, derivative_x)
        gradient_angles = np.degrees(gradient_radians)  # radians * 180 / pi
        gradient_angles[gradient_angles < 0] += 180

        # Put all angles in 4 bins, corresponding to their approximate direction
        gradient_angles = np.where((((0 <= gradient_angles) & (gradient_angles < 22.5)) |
                                   ((157.5 <= gradient_angles) & (gradient_angles <= 180))), 0, gradient_angles)
        gradient_angles = np.where((22.5 <= gradient_angles) & (gradient_angles < 67.5), 45, gradient_angles)
        gradient_angles = np.where((67.5 <= gradient_angles) & (gradient_angles < 112.5), 90, gradient_angles)
        gradient_angles = np.where((112.5 <= gradient_angles) & (gradient_angles < 157.5), 135, gradient_angles)

        suppressed = gradient_magnitude.copy()
        # Zero out the border of the image, since they can't contain any edges
        suppressed[0, :] = suppressed[-1, :] = suppressed[:, 0] = suppressed[:, -1] = 0

        for px in range(1, height - 1):
            for py in range(1, width - 1):
                current_magnitude = gradient_magnitude[px, py]
                current_angle = gradient_angles[px, py]

                # Determine the pixels on the same direction as the current pixel
                if current_angle == 0:     # 0' and 180' directions
                    same_direction_pixel_1 = gradient_magnitude[px, py + 1]
                    same_direction_pixel_2 = gradient_magnitude[px, py - 1]
                elif current_angle == 45:  # 45' direction
                    same_direction_pixel_1 = gradient_magnitude[px + 1, py - 1]
                    same_direction_pixel_2 = gradient_magnitude[px - 1, py + 1]
                elif current_angle == 90:  # 90' direction
                    same_direction_pixel_1 = gradient_magnitude[px + 1, py]
                    same_direction_pixel_2 = gradient_magnitude[px - 1, py]
                elif current_angle == 135: # 135' direction
                    same_direction_pixel_1 = gradient_magnitude[px - 1, py - 1]
                    same_direction_pixel_2 = gradient_magnitude[px + 1, py + 1]

                # Suppress the current pixel if not maximum among neighbours on same direction
                if current_magnitude < same_direction_pixel_1 or current_magnitude < same_direction_pixel_2:
                    suppressed[px, py] = 0

        if method == 'non-max suppression':
            return [suppressed.astype(np.uint8)]

        ### Hysteresis-Thresholding step
        # Thresholds are determined automatically, based on percentiles from the gradient magnitudes
        sigma = 0.33
        if count == 'standard':
            percentile = 75
        elif count == 'many':
            percentile = 50

        while True:
            percentile_value = np.percentile(gradient_magnitude, percentile)
            if percentile_value == 0:
                percentile += 1
            else:
                break

        lower_threshold = int(max(0, percentile_value * (1 - sigma * 1.5)))
        upper_threshold = int(min(255, percentile_value * (1 + sigma)))

        weak_intensity = 25
        strong_intensity = 255

        # Double Thresholding is performed -- pixels having gradient intensity higher than
        # upper_threshold are considered strong edges, those with an intensity lower than
        # lower_threshold are considered weak edges and zeroed out and the rest are labeled as weak
        thresholded = np.where(suppressed >= upper_threshold, strong_intensity, suppressed)
        thresholded = np.where(thresholded < lower_threshold, 0, thresholded)
        thresholded = np.where((thresholded >= lower_threshold) &
                                (thresholded < upper_threshold), weak_intensity, thresholded)

        # Hysteresis -- weak edge pixels are labeled as strong if they have at least one strong
        # surrounding pixel
        mask_x, mask_y = np.where(thresholded == weak_intensity)
        mask = np.array(list(zip(mask_x, mask_y)))

        for [x, y] in mask:
            try:
                pixel_neighbourhood_maximum = thresholded[x - 1 : x + 2, y - 1 : y + 2].max()
                if pixel_neighbourhood_maximum == strong_intensity:
                    thresholded[x, y] = strong_intensity
                else:
                    thresholded[x, y] = 0
            except IndexError:
                pass

        return [thresholded.astype(np.uint8)]

def emboss(image, extra_inputs, parameters):
    '''Applies an **Emboss Filter** onto an image. \n

    Arguments:
        *image* (NumPy array) -- the image to be filtered

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *direction* (str) -- the direction of the embossing; possible values
            are *horizontal*, *vertical* and *diagonal*

            *type* (str) -- the type of resulting image; possible values are
            *mask* and *filter*
    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    # Parameters extraction
    direction = parameters['direction']
    type = parameters['type']
    
    if direction == 'horizontal':
        if type == 'mask':
            kernel_1 = np.array([[0, 1, 0], [0, 0, 0], [0, -1, 0]])
            kernel_2 = np.array([[0, -1, 0], [0, 0, 0], [0, 1, 0]])
        elif type == 'filter':
            kernel_1 = np.array([[0, 1, 0], [0, 1, 0], [0, -1, 0]])
            kernel_2 = np.array([[0, -1, 0], [0, 1, 0], [0, 1, 0]])
    elif direction == 'vertical':
        if type == 'mask':
            kernel_1 = np.array([[0, 0, 0], [-1, 0, 1], [0, 0, 0]])
            kernel_2 = np.array([[0, 0, 0], [1, 0, -1], [0, 0, 0]])
        elif type == 'filter':
            kernel_1 = np.array([[0, 0, 0], [-1, 1, 1], [0, 0, 0]])
            kernel_2 = np.array([[0, 0, 0], [1, 1, -1], [0, 0, 0]])

    temp_1 = helpers.apply_kernel(image, kernel_1)
    temp_2 = helpers.apply_kernel(image, kernel_2)
    result = temp_1 + temp_2

    return [result]

def sketch(image, extra_inputs, parameters):
    '''Converts an image to a pencil sketch. \n

    Arguments:
        *image* (NumPy array) -- the image to be sketchified

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *pencil_Stroke_Size* (str, optional) -- the strength of the applied
            blur; possible values are *small*, *medium* and *large*; default
            value is *strong*

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    '''
    # Parameter extraction
    if 'pencil_Stroke_Size' in parameters:
        blur_strength = parameters['pencil_Stroke_Size']
    else:
        blur_strength = 'strong'
    
    if blur_strength == 'small':
        blur_strength = 'weak'
    elif blur_strength == 'large':
        blur_strength = 'strong'

    # The input image is converted (if necessary) to grayscale, inverted and then blurred
    # Since the Colour Dodge technique divides image by inverted mask, the inverted blur
    # would become the normal blur, so we directly pass the blurred image for division
    if utils.is_color(image):
        grayed_image = grayscale(image, {}, {})[0]
    else:
        grayed_image = image.copy()

    blurred_image = blur(grayed_image, {}, {'strength': blur_strength})[0]

    # The blurred and grayscale images are blended using Colour Dodge
    sketched_image = np.where(blurred_image == 0, 0, (grayed_image * 256) / blurred_image)
    sketched_image[sketched_image > 255] = 255

    return [sketched_image.astype(np.uint8)]
