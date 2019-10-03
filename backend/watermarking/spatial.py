"""
Created on Thu Oct  3 19:50:10 2019

@author: Bogdan
"""
import os
import sys
project_path = os.getcwd()
while os.path.basename(project_path) != 'image-tinkering':
    project_path = os.path.dirname(project_path)
sys.path.append(project_path)
from backend import utils


def test():
    pass
