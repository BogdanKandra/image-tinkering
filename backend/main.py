import cv2
import numpy as np
import basic_operations as ops
import time

# Read the input image
imagePath = '../webui/static/testinputs/brontosaur.jpg' # Grayscale
#imagePath = '../webui/static/testinputs/chocolate.png' # Alpha channel
#imagePath = '../webui/static/testinputs/lena.tiff' # TIFF format
#imagePath = '../webui/static/testinputs/wide.jpg' # 4K image

image = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)

# Display results
cv2.imshow('Original Image', image)

cv2.waitKey()
cv2.destroyAllWindows()
