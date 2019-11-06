import cv2
import os
import numpy as np
import miscellaneous.lego as lego


# Read the input image
#image_path = '../webui/static/testinputs/brontosaur.jpg' # Grayscale
#image_path = '../webui/static/testinputs/chocolate.png'  # Alpha channel
#image_path = '../webui/static/testinputs/lena.tiff'      # TIFF format
#image_path = '../webui/static/testinputs/wide.jpg'       # 4K image
image_path = '../webui/static/testinputs/mandrill.tiff'

image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

extra_inputs = {
    }

params = {
    }

result = lego.photomosaic(image, extra_inputs, params)[0]

cv2.imshow('Test', result)
#cv2.imwrite('test.jpg', result)

cv2.waitKey()
cv2.destroyAllWindows()
