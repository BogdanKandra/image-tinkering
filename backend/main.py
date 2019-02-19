import cv2
import numpy as np
import filtering as f

# Read the input image
imagePath = 'inputs/flag.jpg'
image = cv2.imread(imagePath)

# Automatically compute the cutoff frequency
imageH, imageW = image.shape[:2]
if imageH < imageW:
    cutoff = 0.2 * imageH
else:
    cutoff = 0.2 * imageW

# Filter the image
#lowFilteredImageIdeal = f.low_pass(image, cutoff, 'ideal')
#lowFilteredImageButter = f.low_pass(image, cutoff, 'butterworth')
#lowFilteredImageGauss = f.low_pass(image, cutoff, 'gaussian')
#highFilteredImageIdeal = f.high_pass(image, cutoff, 1, 1, 'ideal')
#highFilteredImageButter = f.high_pass(image, cutoff, 1, 1, 'butterworth')
highFilteredImageGauss = f.high_pass(image, cutoff, 1, 1, 'gaussian')
#f30 = f.high_pass(image, 30, 'gaussian')
#f60 = f.high_pass(image, 60, 'gaussian')
#f160 = f.high_pass(image, 160, 'gaussian')
#laplacianImage = f.high_pass(image, 0, 'laplacian')

#imageH, imageW = image.shape[:2] # Take image dimensions
#diffImage = np.zeros((imageH, imageW, 3), np.uint8)

#for px in range(imageH):
#    for py in range(imageW):
#        for ch in range(3):
#            diff = image.item((px, py, ch)) - laplacianImage.item((px, py, ch))
#            if diff < 0:
#                diffImage.itemset((px, py, ch), 0)
#            else:
#                diffImage.itemset((px, py, ch), diff)

# Display results
cv2.imshow('Original Image', image)
#cv2.imshow('Ideal Low Pass Filtered Image', lowFilteredImageIdeal)
#cv2.imshow('Butterworth Low Pass Filtered Image', lowFilteredImageButter)
#cv2.imshow('Gaussian Low Pass Filtered Image', lowFilteredImageGauss)
#cv2.imshow('Ideal High Pass Filtered Image', highFilteredImageIdeal)
#cv2.imshow('Butterworth High Pass Filtered Image', highFilteredImageButter)
cv2.imshow('Gaussian High Pass Filtered Image', highFilteredImageGauss)
#cv2.imshow('f30', f30)
#cv2.imshow('f60', f60)
#cv2.imshow('f160', f160)
#cv2.imshow('Laplacian Image', laplacianImage)
#cv2.imshow('Diff', diffImage)
cv2.waitKey()
cv2.destroyAllWindows()
