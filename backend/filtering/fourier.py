import os
import sys
import pickle
import cv2
import numpy as np
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def ideal_filter(mode, size, cutoff):
    """Generates an **Ideal Filter** which filters out frequencies
    higher (*low-pass*) or lower (*high-pass*) than the cutoff frequency\n
    It has the following transfer function:\n
        *low-pass mode:* H(u,v) = 1, if D(u,v) <= cutoff; 0, otherwise\n
        *high-pass mode:* H(u,v) = 0, if D(u,v) <= cutoff; 1, otherwise\n

    Arguments:
        *mode* (str) -- specifies whether low-pass or high-pass filtering is desired

        *size* (2-tuple) -- a tuple specifying the size of the filter to be
        generated

        *cutoff* (int) -- the maximum / minimum frequency to be let through by the filter
    Returns:
        NumPy array uint8 -- the filter image
    """
    center = np.asarray([size[0] // 2, size[1] // 2])  # Center of the filter

    I, J = np.ogrid[:size[0], :size[1]]
    p, q = I - center[0], J - center[1]
    distances = np.sqrt(p**2 + q**2)

    if mode == 'low':
        filter_image = np.where(distances <= cutoff, 1, 0)
    else:
        filter_image = np.where(distances > cutoff, 1, 0)

    return filter_image

def butterworth_filter(mode, size, cutoff, order=2):
    """Generates a **Butterworth Filter** which has the transfer function:\n
        *low-pass mode:*   H(u,v) = 1 / [1 + (D(u,v) / cutoff) ^ (2 * order)] \n
        *high-pass mode:*  H(u,v) = 1 / [1 + (cutoff / D(u,v)) ^ (2 * order)]

    Arguments:
        *mode* (str) -- specifies whether low-pass or high-pass filtering is desired

        *size* (2-tuple) -- a tuple specifying the size of the filter to be
        generated

        *cutoff* (int) -- *for low-pass mode*, the frequency after which the pixel
        values will decrease gradually towards zero (the speed of the decrease
        depends on the order)

        *order* (int) -- the increase of the order is directly proportional
        with the decrease of the output pixel intensity; higher orders result
        in an increased ringing effect in the blurring

    Returns:
        NumPy array float64 -- the filter image
    """
    order_term = 2 * order
    center = np.asarray([size[0] // 2, size[1] // 2])

    I, J = np.ogrid[:size[0], :size[1]]
    p, q = I - center[0], J - center[1]
    distances = np.sqrt(p**2 + q**2)

    if mode == 'low':
        filter_image = np.divide(1, np.add(1, np.power(distances / cutoff, order_term)))
    else:
        filter_image = np.divide(1, np.add(1, np.power(cutoff / distances, order_term)))

    return filter_image

def gaussian_filter(mode, size, cutoff):
    """Generates a **Gaussian Filter** which has the transfer function:\n
        *low-pass mode:*   H(u,v) = e ^ (-Duv^2 / 2 * cutoff ^ 2) \n
        *high-pass mode:*  H(u,v) = 1 - e ^ (-Duv^2 / 2 * cutoff ^ 2)

    Arguments:
        *mode* (str) -- specifies whether low-pass or high-pass filtering is desired

        *size* (2-tuple) -- a tuple specifying the size of the filter to be
        generated

        *cutoff* (int) -- for low-pass mode, the frequency after which the
        pixel values will decrease gradually towards zero

    Returns:
        NumPy array float64 -- the filter image
    """
    cutoff_term = 2 * (cutoff ** 2)
    center = np.asarray([size[0] // 2, size[1] // 2])

    I, J = np.ogrid[:size[0], :size[1]]
    p, q = I - center[0], J - center[1]
    distances_squared = p**2 + q**2
    distances = -1 * distances_squared
    filter_image = np.power(np.e, distances / cutoff_term)

    if mode == 'low':
        return filter_image

    return 1 - filter_image

def low_pass(image, extra_inputs, parameters):
    """Applies a **Low Pass Filter** on an image. \n
    The image is converted into the frequency domain (using the *Fast Fourier
    Transform*) and only the frequencies smaller than the cutoff frequency are
    let through.

    Arguments:
        *image* (NumPy array) -- the image on which the filter is to be applied

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *cutoff* (int) -- the maximum frequency to be let through by the filter

            *type* (str, optional) -- the type of low-pass filter to be applied;
            possible values are: *ideal*, *butterworth*, *gaussian* and default
            value is *gaussian*

            *order* (int, optional) -- the order used for Butterworth filtering;
            default value is 2

            *filename* (str, optional) -- the name of the image file to be filtered,
            used for checking whether the corresponding FFT(s) are serialized on the server or not

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    """
    # Parameter validation and assignment
    if 'type' in parameters:
        filter_type = parameters['type']
    else:
        filter_type = 'gaussian'

    if 'order' in parameters:
        order = parameters['order']
    else:
        order = 2

    if 'filename' in parameters:
        filename = parameters['filename']
    else:
        filename = ''

    image_h, image_w = image.shape[:2]          # Take image dimensions

    # Compute the cutoff frequency as a percentage from the smaller dimension of the image
    cutoff_dimension = image_h if image_h < image_w else image_w
    cutoff = parameters['cutoff'] / 100 * cutoff_dimension

    padded_h, padded_w = 2 * image_h, 2 * image_w # Obtain the padding parameters

    # Check whether the FFTs of the image have been serialized or not
    deserializing, file_not_found = False, False
    pickles_path = os.path.join(project_path, 'webui', 'static', 'tempdata')

    if filename != '':
        filename, extension = filename.split('.')
        if utils.is_color(image):
            files_to_check = [filename + '_' + c + '_fft.pickle' for c in 'bgr']
        else:
            files_to_check = [filename + '_fft.pickle']
        for file in files_to_check:
            if not os.path.isfile(os.path.join(pickles_path, file)):
                file_not_found = True
        if not file_not_found:
            deserializing = True

    # Deserialize the FFTs if possible
    if deserializing:
        padded_image_FFTs = []
        for file_name in files_to_check:
            file = open(os.path.join(pickles_path, file_name), 'rb')
            padded_image_FFTs.append(pickle.load(file))
            file.close()
    else:
        # Create padded image
        if utils.is_color(image):
            padded_image = np.zeros((padded_h, padded_w, len(utils.get_channels(image))), np.uint8)
            padded_image[0:image_h, 0:image_w, :] = image
        else:
            padded_image = np.zeros((padded_h, padded_w), np.uint8)
            padded_image[0:image_h, 0:image_w] = image

        # Take the FFTs of the padded image channels
        padded_image_FFTs = utils.get_FFTs(padded_image)

    # Compute the filter image
    if filter_type == 'ideal':
        filter_image = ideal_filter('low', (padded_h, padded_w), cutoff)
    elif filter_type == 'butterworth':
        filter_image = butterworth_filter('low', (padded_h, padded_w), cutoff, order)
    elif filter_type == 'gaussian':
        filter_image = gaussian_filter('low', (padded_h, padded_w), cutoff)

    # Apply the filter to the FFTs
    filtered_FFTs = [np.multiply(channelFFT, filter_image) for channelFFT in padded_image_FFTs]

    # Take the inverse FFT of the filtered padded image FFT components
    result_components = [np.real(np.fft.ifft2(np.fft.ifftshift(filteredComponent)))
                         for filteredComponent in filtered_FFTs]

    # Obtain the result image
    if len(result_components) == 1:
        result_image = result_components[0]
    else:
        result_image = cv2.merge(result_components)

    # Trim values lower than 0 or higher than 255
    result_image = np.where(result_image > 255, 255, result_image)
    result_image = np.where(result_image < 0, 0, result_image)

    # Round the values and unpad the image
    result_image = np.uint8(np.rint(result_image))
    if len(result_components) == 1:
        result_image = result_image[0:image_h, 0:image_w]
    else:
        result_image = result_image[0:image_h, 0:image_w, :]

    return [result_image]

def high_pass(image, extra_inputs, parameters):
    """Applies a **High Pass Filter** on an image. \n
    The image is converted into the frequency domain (using the *Fast Fourier
    Transform*) and only the frequencies higher than the cutoff frequency are
    let through. *High-frequency emphasis* can be achieved by providing an *offset*
    greater than 0 (0 is default) and a *multiplier* greater than 1 (1 is default).
    The filter is then transformed by the equation:
        emphasisFilter = offset + multiplier * highpassFilter

    Arguments:
        *image* (NumPy array) -- the image on which the filter is to be applied

        *extra_inputs* (dictionary) -- a dictionary holding any extra inputs for the call (empty)

        *parameters* (dictionary) -- a dictionary containing following keys:

            *cutoff* (int) -- the minimum frequency to be let through by the filter

            *offset* (int, optional) -- number used for avoiding the reduction
            of the DC term to 0; default value is 0, which does not prevent
            reduction of the DC term

            *multiplier* (int, optional) -- number used for emphasizing
            frequencies; default value is 1, which does not have any effect

            *type* (str, optional) -- the type of high-pass filter to be applied;
            possible values are: *ideal*, *butterworth*, *gaussian*; default
            value is *gaussian*

            *order* (int, optional) -- the order used for Butterworth filtering;
            default value is 2

            *filename* (str, optional) -- the name of the image file to be
            filtered, used for checking whether the corresponding FFT(s) are
            serialized on the server or not

    Returns:
        list of NumPy array uint8 -- list containing the filtered image
    """
    # Parameter validation and assignment
    if 'offset' in parameters:
        offset = parameters['offset']
    else:
        offset = 0

    if 'multiplier' in parameters:
        multiplier = parameters['multiplier']
    else:
        multiplier = 1

    if 'type' in parameters:
        filter_type = parameters['type']
    else:
        filter_type = 'gaussian'

    if 'order' in parameters:
        order = parameters['order']
    else:
        order = 2

    if 'filename' in parameters:
        filename = parameters['filename']
    else:
        filename = ''

    image_h, image_w = image.shape[:2]          # Take image dimensions

    # Compute the cutoff frequency as a percentage from the smaller dimension of the image
    cutoff_dimension = image_h if image_h < image_w else image_w
    cutoff = parameters['cutoff'] / 100 * cutoff_dimension

    padded_h, padded_w = 2 * image_h, 2 * image_w # Obtain the padding parameters

    # Check whether the FFTs of the image have been serialized or not
    deserializing, file_not_found = False, False
    pickles_path = os.path.join(project_path, 'webui', 'static', 'tempdata')

    if filename != '':
        filename, extension = filename.split('.')
        if utils.is_color(image):
            files_to_check = [filename + '_' + c + '_fft.pickle' for c in 'bgr']
        else:
            files_to_check = [filename + '_fft.pickle']
        for file in files_to_check:
            if not os.path.isfile(os.path.join(pickles_path, file)):
                file_not_found = True
        if not file_not_found:
            deserializing = True

    # Deserialize the FFTs if possible
    if deserializing:
        padded_image_FFTs = []
        for file in files_to_check:
            f = open(os.path.join(pickles_path, file), 'rb')
            padded_image_FFTs.append(pickle.load(f))
            f.close()
            print('Deserialized', file)
    else:
        # Create padded image
        if utils.is_color(image):
            padded_image = np.zeros((padded_h, padded_w, len(utils.get_channels(image))), np.uint8)
            padded_image[0:image_h, 0:image_w, :] = image
        else:
            padded_image = np.zeros((padded_h, padded_w), np.uint8)
            padded_image[0:image_h, 0:image_w] = image

        # Take the FFTs of the padded image channels
        padded_image_FFTs = utils.get_FFTs(padded_image)

    # Compute the filter image
    if filter_type == 'ideal':
        filter_image = ideal_filter('high', (padded_h, padded_w), cutoff)
    elif filter_type == 'butterworth':
        filter_image = butterworth_filter('high', (padded_h, padded_w), cutoff, order)
    elif filter_type == 'gaussian':
        filter_image = gaussian_filter('high', (padded_h, padded_w), cutoff)

	# Perform High-frequency emphasis
    if multiplier == 1:
        filter_image = offset + filter_image
    else:
        filter_image = offset + np.multiply(multiplier, filter_image)

    # Apply the filter to the FFTs
    filtered_FFTs = [np.multiply(channelFFT, filter_image) for channelFFT in padded_image_FFTs]

    # Take the inverse FFT of the filtered padded image FFT components
    result_components = [np.real(np.fft.ifft2(np.fft.ifftshift(filteredComponent)))
                         for filteredComponent in filtered_FFTs]

    # Obtain the result image
    if len(result_components) == 1:
        result_image = result_components[0]
    else:
        result_image = cv2.merge(result_components)

    # Trim values lower than 0 or higher than 255
    result_image = np.where(result_image > 255, 255, result_image)
    result_image = np.where(result_image < 0, 0, result_image)

    # Round the values and unpad the image
    result_image = np.uint8(np.rint(result_image))
    if len(result_components) == 1:
        result_image = result_image[0:image_h, 0:image_w]
    else:
        result_image = result_image[0:image_h, 0:image_w, :]

    return [result_image]
