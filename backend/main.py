import cv2
import numpy as np
import filtering.fourier as f
import basic_operations as ops
import time

# Read the input image
imagePath = '../webui/static/testinputs/brontosaur.jpg' # Grayscale
#imagePath = '../webui/static/testinputs/chocolate.png' # Alpha channel
#imagePath = '../webui/static/testinputs/lena.tiff' # TIFF format
#imagePath = '../webui/static/testinputs/wide.jpg' # 4K image

image = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)

# Automatically compute the cutoff frequency
imageH, imageW = image.shape[:2]
if imageH < imageW:
    cutoff = 0.2 * imageH
else:
    cutoff = 0.2 * imageW

paramsGaussian = {
        'cutoff': cutoff,
        'type': 'gaussian'
        }

paramsButterworth = {
        'cutoff': cutoff,
        'offset': 1,
        'type': 'butterworth',
        'filename': 'bars_15557613543664565.png'
        }

# Filter the image
#lowFilteredImageGauss = f.low_pass(image, paramsGaussian)
#highFilteredImageButter = f.high_pass(image, paramsButterworth)

# Display results
cv2.imshow('Original Image', image)
#cv2.imshow('Gaussian Low Pass Filtered Image', lowFilteredImageGauss)
#cv2.imshow('Butterworth High Pass Filtered Image', highFilteredImageButter)

cv2.waitKey()
cv2.destroyAllWindows()
