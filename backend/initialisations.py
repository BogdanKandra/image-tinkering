"""
Created on Sun Mar 10 15:12:37 2019

@author: Bogdan
"""
import cv2
import numpy as np

def compute_RGB(image):
    pass
    
impath = '../webui/static/testinputs/flag.jpg'
impath2 = '../webui/static/testinputs/gray.png'
im = cv2.imread(impath, cv2.CV_LOAD_IMAGE_ANYDEPTH)

#B, G, R = cv2.split(im)
#if (B == G).all() and (G == R).all():
#    print('Gray')
#else:
#    print('Color')



#sh = len(im.shape)
#print(im.shape)
#compute_RGB(im)