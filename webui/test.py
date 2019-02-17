"""
Created on Sun Feb 17 15:16:17 2019

@author: Bogdan
"""
import magic

mime = magic.Magic(mime=True)
mimeType = mime.from_file('TODOs.pdf')
print(mimeType)
