import cv2
import numpy as np
import filtering.fourier as f
import basic_operations as ops
import time

# Read the input image
#imagePath = '../webui/static/testinputs/brontosaur.jpg'
imagePath = '../webui/static/testinputs/bars.png'
#imagePath = '../webui/static/testinputs/flag.jpg'
image = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)

# Automatically compute the cutoff frequency
imageH, imageW = image.shape[:2]
if imageH < imageW:
    cutoff = 0.2 * imageH
else:
    cutoff = 0.2 * imageW

# Filter the image
lowFilteredImageIdeal = f.low_pass(image, cutoff, 'ideal')
lowFilteredImageButter = f.low_pass(image, cutoff, 'butterworth')
lowFilteredImageGauss = f.low_pass(image, cutoff, 'gaussian')
#highFilteredImageIdeal = f.high_pass(image, cutoff, 1, 1, 'ideal', filename='bars_15557613543664565.png')
#highFilteredImageButter = f.high_pass(image, cutoff, 1, 1, 'butterworth', filename='bars_15557613543664565.png')
#highFilteredImageGauss = f.high_pass(image, cutoff, 1, 1, 'gaussian', filename='bars_15557613543664565.png')

# Display results
cv2.imshow('Original Image', image)
cv2.imshow('Ideal Low Pass Filtered Image', lowFilteredImageIdeal)
cv2.imshow('Butterworth Low Pass Filtered Image', lowFilteredImageButter)
cv2.imshow('Gaussian Low Pass Filtered Image', lowFilteredImageGauss)
#cv2.imshow('Ideal High Pass Filtered Image', highFilteredImageIdeal)
#cv2.imshow('Butterworth High Pass Filtered Image', highFilteredImageButter)
#cv2.imshow('Gaussian High Pass Filtered Image', highFilteredImageGauss)

cv2.waitKey()
cv2.destroyAllWindows()
