import os, sys
import pickle
import cv2
import numpy as np
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(os.path.join(projectPath))
from backend import basic_operations as ops

    
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
    v = np.asarray([size[0] // 2, size[1] // 2])  # Center of the filter
    
    I, J = np.ogrid[:size[0], :size[1]]
    p, q = I - v[0], J - v[1]
    Duvs = np.sqrt(p**2 + q**2)

    if mode == 'low':
        filterImage = np.where(Duvs <= cutoff, 1, 0)
    else:
        filterImage = np.where(Duvs > cutoff, 1, 0)
    
    return filterImage

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
    orderTerm = 2 * order
    v = np.asarray([size[0] // 2, size[1] // 2])
    
    I, J = np.ogrid[:size[0], :size[1]]
    p, q = I - v[0], J - v[1]
    Duvs = np.sqrt(p**2 + q**2)
    if mode == 'low':
        filterImage = np.divide(1, np.add(1, np.power(Duvs / cutoff, orderTerm)))
    else:
        filterImage = np.divide(1, np.add(1, np.power(cutoff / Duvs, orderTerm)))
        
    return filterImage

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
    cutoffTerm = 2 * (cutoff ** 2)
    v = np.asarray([size[0] // 2, size[1] // 2])
    
    I, J = np.ogrid[:size[0], :size[1]]
    p, q = I - v[0], J - v[1]
    Duvs_squared = p**2 + q**2
    distances = -1 * Duvs_squared
    filterImage = np.power(np.e, distances / cutoffTerm)
    if mode == 'low':
        return filterImage
    else:
        return 1 - filterImage

def low_pass(image, parameters):
    """Applies a **Low Pass Filter** on an image. \n
    The image is converted into the frequency domain (using the *Fast Fourier
    Transform*) and only the frequencies smaller than the cutoff frequency are
    let through.
    
    Arguments:
        *image* (NumPy array) -- the image on which the filter is to be applied

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
        NumPy array uint8 -- the filtered image
    """
    
    # Parameter validation and assignment
    cutoff = parameters['cutoff']
    
    if 'type' in parameters:
        type = parameters['type']
    else:
        type = 'gaussian'
    
    if 'order' in parameters:
        order = parameters['order']
    else:
        order = 2
        
    if 'filename' in parameters:
        filename = parameters['filename']
    else:
        filename = ''
    
    imageH, imageW = image.shape[:2]          # Take image dimensions
    paddedH, paddedW = 2 * imageH, 2 * imageW # Obtain the padding parameters

    # Check whether the FFTs of the image have been serialized or not
    deserializing, file_not_found = False, False
    pickles_path = os.path.join(projectPath, 'webui', 'static', 'tempdata')

    if filename != '':
        filename, extension = filename.split('.')
        if ops.isColor(image):
            files_to_check = [filename + '_' + c + '_fft.pickle' for c in 'bgr']
        else:
            files_to_check = [filename + '_fft.pickle']
        for file in files_to_check:
            if not os.path.isfile(os.path.join(pickles_path, file)):
                file_not_found = True
        if file_not_found == False:
            deserializing = True
    
    # Deserialize the FFTs if possible
    if deserializing:
        paddedImageFFTs = []
        for file in files_to_check:
            f = open(os.path.join(pickles_path, file), 'rb')
            paddedImageFFTs.append(pickle.load(f))
            f.close()
    else:
        # Create padded image
        if ops.isColor(image):
            paddedImage = np.zeros((paddedH, paddedW, 3), np.uint8)
            paddedImage[0:imageH, 0:imageW, :] = image
        else:
            paddedImage = np.zeros((paddedH, paddedW), np.uint8)
            paddedImage[0:imageH, 0:imageW] = image

        # Take the FFTs of the padded image channels
        paddedImageFFTs = ops.getFFTs(paddedImage)
    
    # Compute the filter image
    if type == 'ideal':
        filterImage = ideal_filter('low', (paddedH, paddedW), cutoff)
    elif type == 'butterworth':
        filterImage = butterworth_filter('low', (paddedH, paddedW), cutoff, order)
    elif type == 'gaussian':
        filterImage = gaussian_filter('low', (paddedH, paddedW), cutoff)

    # Apply the filter to the FFTs
    filteredFFTs = [np.multiply(channelFFT, filterImage) for channelFFT in paddedImageFFTs]
    
    # Take the inverse FFT of the filtered padded image FFT components
    resultComponents = [np.real(np.fft.ifft2(np.fft.ifftshift(filteredComponent))) 
                        for filteredComponent in filteredFFTs]
    
    # Obtain the result image
    if len(resultComponents) == 3:
        resultImage = cv2.merge(resultComponents)
    else:
        resultImage = resultComponents[0]

    # Trim values lower than 0 or higher than 255
    resultImage = np.where(resultImage > 255, 255, resultImage)
    resultImage = np.where(resultImage < 0, 0, resultImage)
    
    # Round the values and unpad the image
    resultImage = np.uint8(np.rint(resultImage))
    if len(resultComponents) == 3:
        resultImage = resultImage[0:imageH, 0:imageW, :]
    else:
        resultImage = resultImage[0:imageH, 0:imageW]

    return resultImage

def high_pass(image, parameters):
    """Applies a **High Pass Filter** on an image. \n
    The image is converted into the frequency domain (using the *Fast Fourier
    Transform*) and only the frequencies higher than the cutoff frequency are
    let through. *High-frequency emphasis* can be achieved by providing an *offset*
    greater than 0 (0 is default) and a *multiplier* greater than 1 (1 is default).
    The filter is then transformed by the equation:
        emphasisFilter = offset + multiplier * highpassFilter
    
    Arguments:
        *image* (NumPy array) -- the image on which the filter is to be applied
        
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
        NumPy array uint8 -- the filtered image
    """
    
    # Parameter validation and assignment
    cutoff = parameters['cutoff']
    
    if 'offset' in parameters:
        offset = parameters['offset']
    else:
        offset = 0
        
    if 'multiplier' in parameters:
        multiplier = parameters['multiplier']
    else:
        multiplier = 1
    
    if 'type' in parameters:
        type = parameters['type']
    else:
        type = 'gaussian'
    
    if 'order' in parameters:
        order = parameters['order']
    else:
        order = 2
        
    if 'filename' in parameters:
        filename = parameters['filename']
    else:
        filename = ''
    
    imageH, imageW = image.shape[:2]          # Take image dimensions
    paddedH, paddedW = 2 * imageH, 2 * imageW # Obtain the padding parameters

    # Check whether the FFTs of the image have been serialized or not
    deserializing, file_not_found = False, False
    pickles_path = os.path.join(projectPath, 'webui', 'static', 'tempdata')

    if filename != '':
        filename, extension = filename.split('.')
        if ops.isColor(image):
            files_to_check = [filename + '_' + c + '_fft.pickle' for c in 'bgr']
        else:
            files_to_check = [filename + '_fft.pickle']
        for file in files_to_check:
            if not os.path.isfile(os.path.join(pickles_path, file)):
                file_not_found = True
        if file_not_found == False:
            deserializing = True

    # Deserialize the FFTs if possible
    if deserializing:
        paddedImageFFTs = []
        for file in files_to_check:
            f = open(os.path.join(pickles_path, file), 'rb')
            paddedImageFFTs.append(pickle.load(f))
            f.close()
            print('Deserialized', file)
    else:
        # Create padded image
        if ops.isColor(image):
            paddedImage = np.zeros((paddedH, paddedW, 3), np.uint8)
            paddedImage[0:imageH, 0:imageW, :] = image
        else:
            paddedImage = np.zeros((paddedH, paddedW), np.uint8)
            paddedImage[0:imageH, 0:imageW] = image
        
        # Take the FFTs of the padded image channels
        paddedImageFFTs = ops.getFFTs(paddedImage)

    # Compute the filter image
    if type == 'ideal':
        filterImage = ideal_filter('high', (paddedH, paddedW), cutoff)
    elif type == 'butterworth':
        filterImage = butterworth_filter('high', (paddedH, paddedW), cutoff, order)
    elif type == 'gaussian':
        filterImage = gaussian_filter('high', (paddedH, paddedW), cutoff)

	# Perform High-frequency emphasis
    if multiplier == 1:
        filterImage = offset + filterImage
    else:
        filterImage = offset + np.multiply(multiplier, filterImage)

    # Apply the filter to the FFTs
    filteredFFTs = [np.multiply(channelFFT, filterImage) for channelFFT in paddedImageFFTs]
    
    # Take the inverse FFT of the filtered padded image FFT components
    resultComponents = [np.real(np.fft.ifft2(np.fft.ifftshift(filteredComponent))) 
                        for filteredComponent in filteredFFTs]
    
    # Obtain the result image
    if len(resultComponents) == 3:
        resultImage = cv2.merge(resultComponents)
    else:
        resultImage = resultComponents[0]

    # Trim values lower than 0 or higher than 255
    resultImage = np.where(resultImage > 255, 255, resultImage)
    resultImage = np.where(resultImage < 0, 0, resultImage)
    
    # Round the values and unpad the image
    resultImage = np.uint8(np.rint(resultImage))
    if len(resultComponents) == 3:
        resultImage = resultImage[0:imageH, 0:imageW, :]
    else:
        resultImage = resultImage[0:imageH, 0:imageW]

    return resultImage
