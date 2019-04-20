import os, sys
import numpy as np
from matplotlib import pyplot as plt
import cv2
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(os.path.join(projectPath))
from backend import basic_operations as ops

def fft_plot(image, cmap=None):
    """Takes a frequency domain image and displays its spectrum.

    Arguments:
        image (numPy array) -- the image to be displayed
        
        cmap (str) -- optional, the color map to be used; default value is None

    Returns:
        Nothing
    """
    
    # Take the magnitudes and reduce values by logarithming
    magnitudes = np.log(np.abs(image) + 1)
    
    plt.figure()
    plt.imshow(magnitudes, cmap)
    plt.show()
    
def ideal_filter(mode, size, cutoff):
    """Generates an **Ideal Filter** which filters out frequencies 
    higher (*low-pass*) or lower (*high-pass*) than the cutoff frequency\n
    The transfer function for low-pass filtering is:
        H(u,v) = 1, if D(u,v) <= cutoff \n
               = 0, otherwise\n
    for high-pass filtering:
        H(u,v) = 0, if D(u,v) <= cutoff \n
               = 1, otherwise
    
    Arguments:
        *mode* (str) -- specifies whether low-pass or high-pass filtering is desired
        
        *size* (2-tuple) -- a tuple specifying the size of the filter to be 
        generated
        
        *cutoff* (int) -- the maximum / minimum frequency to be let through by the filter
    Returns:
        NumPy array uint8 -- the filter image
    """
    filterImage = np.zeros(size, np.uint8)
    v = np.asarray([size[0] // 2, size[1] // 2])

    for px in range(0, size[0]):
        for py in range(0, size[1]):
            u = np.asarray([px, py])
            if np.linalg.norm(u - v) <= cutoff and mode == 'low':
                filterImage.itemset((px, py), 1)
            elif np.linalg.norm(u - v) > cutoff and mode == 'high':
                filterImage.itemset((px, py), 1)
    
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
    filterImage = np.zeros(size, np.float64)
    # Compute constants
    orderTerm = 2 * order
    v = np.asarray([size[0] // 2, size[1] // 2])

    for px in range(0, size[0]):
        for py in range(0, size[1]):
            u = np.asarray([px, py])
            Duv = np.linalg.norm(u - v)
            resultLow = 1 / (1 + pow(Duv / cutoff, 2 * orderTerm))
            resultHigh = 1 / (1 + pow(cutoff / Duv, 2 * orderTerm))
            if mode == 'low':
                filterImage.itemset((px, py), resultLow)
            elif mode == 'high':
                filterImage.itemset((px, py), resultHigh)

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
    filterImage = np.zeros(size, np.float64)    
    # Compute constants
    cutoffTerm = 2 * (cutoff ** 2)
    v = np.asarray([size[0] // 2, size[1] // 2])

    for px in range(0, size[0]):
        for py in range(0, size[1]):
            u = np.asarray([px, py])
            Duv = np.linalg.norm(u - v)
            distance = -1 * (Duv ** 2)
            result = pow(np.e, distance / cutoffTerm)
            if mode == 'low':
                filterImage.itemset((px, py), result)
            elif mode == 'high':
                filterImage.itemset((px, py), 1 - result)
    
    return filterImage

def laplacian_filter(size):
    """Generates a **Laplacian Filter** which has the transfer function:\n
    H(u,v) = -4 * pi^2 * Duv^2
    
    Arguments:
        *size* (2-tuple) -- a tuple specifying the size of the filter to be
        generated
    
    Returns:
        NumPy array float64 -- the Laplacian image
    """
    filterImage = np.zeros(size, np.float64)
    # Compute constants
    v = np.asarray([size[0] // 2, size[1] // 2])
    piSquaredTimesFour = -4 * (np.pi ** 2)

    for px in range(0, size[0]):
        for py in range(0, size[1]):
            u = np.asarray([px, py])
            Duv = np.linalg.norm(u - v)
            Huv = piSquaredTimesFour * (Duv ** 2)
            filterImage.itemset((px, py), Huv)
    
    return filterImage

def low_pass(image, cutoff, type):
    """Applies a **Low Pass Filter** on an image. \n
    The image is converted into the frequency domain (using the *Fast Fourier
    Transform*) and only the frequencies smaller than the cutoff frequency are
    let through.
    
    Arguments:
        *image* (NumPy array) -- the image on which the filter is to be applied

        *cutoff* (int) -- the maximum frequency to be let through by the filter
        
        *type* (str) -- the type of low-pass filter to be applied;
        possible values are: *ideal*, *butterworth*, *gaussian*

    Returns:
        NumPy array uint8 -- the filtered image
    """
    
    imageH, imageW = image.shape[:2]          # Take image dimensions
    paddedH, paddedW = 2 * imageH, 2 * imageW # Obtain the padding parameters

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
        filterImage = butterworth_filter('low', (paddedH, paddedW), cutoff)
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
    if len(resultComponents) == 3:
        for px in range(0, paddedH):
            for py in range(0, paddedW):
                for ch in range(0, 3):
                    currentPixel = resultImage.item((px,py,ch))
                    if currentPixel > 255:
                        resultImage.itemset((px,py,ch), 255)
                    elif currentPixel < 0:
                        resultImage.itemset((px,py,ch), 0)
    else:
        for px in range(0, paddedH):
            for py in range(0, paddedW):
                currentPixel = resultImage.item((px,py))
                if currentPixel > 255:
                    resultImage.itemset((px,py), 255)
                elif currentPixel < 0:
                    resultImage.itemset((px,py), 0)
    
    # Round the values and unpad the image
    resultImage = np.uint8(np.rint(resultImage))
    if len(resultComponents) == 3:
        resultImage = resultImage[0:imageH, 0:imageW, :]
    else:
        resultImage = resultImage[0:imageH, 0:imageW]

    # Compute the difference between the original and transformed images
#    diff = cv2.absdiff(image, resultImage)
#    for px in range(imageH):
#        for py in range(imageW):
#            for ch in range(3):
#                if diff.item(px, py, ch) > 0:   # if there is a difference, augment it
#                    diff.itemset((px, py, ch), diff.item(px,py,ch) + 150)

    return resultImage

def high_pass(image, cutoff, offset=0, multiplier=1, type='gaussian'):
    """Applies a **High Pass Filter** on an image. \n
    The image is converted into the frequency domain (using the *Fast Fourier
    Transform*) and only the frequencies higher than the cutoff frequency are
    let through. *High-frequency emphasis* can be achieved by providing an *offset*
    greater than 0 (0 is default) and a *multiplier* greater than 1 (1 is default).
    The filter is then transformed by the equation:
        emphasisFilter = offset + multiplier * highpassFilter
    
    Arguments:
        *image* (NumPy array) -- the image on which the filter is to be applied

        *cutoff* (int) -- the minimum frequency to be let through by the filter
        
        *offset* (int) -- number used for avoiding the reduction of the dc term to 0
        
        *multiplier* (int) -- number used for emphasizing frequencies
        
        *type* (str) -- the type of high-pass filter to be applied;
        possible values are: *ideal*, *butterworth*, *gaussian*

    Returns:
        NumPy array uint8 -- the filtered image
    """
    
    imageH, imageW = image.shape[:2]          # Take image dimensions
    paddedH, paddedW = 2 * imageH, 2 * imageW # Obtain the padding parameters

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
        filterImage = butterworth_filter('high', (paddedH, paddedW), cutoff)
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
    if len(resultComponents) == 3:
        for px in range(0, paddedH):
            for py in range(0, paddedW):
                for ch in range(0, 3):
                    currentPixel = resultImage.item((px,py,ch))
                    if currentPixel > 255:
                        resultImage.itemset((px,py,ch), 255)
                    elif currentPixel < 0:
                        resultImage.itemset((px,py,ch), 0)
    else:
        for px in range(0, paddedH):
            for py in range(0, paddedW):
                currentPixel = resultImage.item((px,py))
                if currentPixel > 255:
                    resultImage.itemset((px,py), 255)
                elif currentPixel < 0:
                    resultImage.itemset((px,py), 0)
    
    # Round the values and unpad the image
    resultImage = np.uint8(np.rint(resultImage))
    if len(resultComponents) == 3:
        resultImage = resultImage[0:imageH, 0:imageW, :]
    else:
        resultImage = resultImage[0:imageH, 0:imageW]

    # Compute the difference between the original and transformed images
#    diff = cv2.absdiff(image, resultImage)
#    for px in range(imageH):
#        for py in range(imageW):
#            for ch in range(3):
#                if diff.item(px, py, ch) > 0:   # if there is a difference, augment it
#                    diff.itemset((px, py, ch), diff.item(px,py,ch) + 150)

    return resultImage