"""
Created on Sun Mar 10 15:12:37 2019

@author: Bogdan
"""
import cv2, pickle


def channels(image):
    """ This function takes an image as parameter and returns a list containing
    its R, G, B channels or the image itself, if it is grayscale
    """
    if len(image.shape) == 2: # Image is grayscale
        return [image]
    else:                     # Image is color
        return cv2.split(image)


impath = '../webui/static/testinputs/flag.jpg'
impath2 = '../webui/static/testinputs/elaine.tiff'
impath3 = '../webui/static/testinputs/brontosaur.jpg'

im = cv2.imread(impath, cv2.IMREAD_UNCHANGED)

#ims = channels(im)
#i = 1
#for image in ims:
#    cv2.imshow('Image ' + str(i), image)
#    i += 1

f = open('test.pickle', 'wb')
pickle.dump(im, f)
f.close()

f = open('test.pickle', 'rb')
im2 = pickle.load(f)
f.close()

cv2.imshow('Image', im2)

cv2.waitKey()
cv2.destroyAllWindows()
