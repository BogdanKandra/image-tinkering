"""
Created on Sun Mar 10 14:33:41 2019

@author: Bogdan
"""
import os, sys
import cv2
from flask.blueprints import Blueprint
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template

# Import backend module
projectPath = os.getcwd()
while os.path.basename(projectPath) != 'ImageTinkering':
    projectPath = os.path.dirname(projectPath)
sys.path.append(os.path.join(projectPath, 'backend'))

from backend import initialisations as init


init_mod = Blueprint('initialisations', __name__, url_prefix='/initialisations')

@init_mod.route('/', methods=['POST'])
def initialise():
    # Primeste lista de nume ale fisierelor care trebuie initializate
    
    files = request.get_json()['files']
    
    for file in files:
        print('File:', file)
        filePath = os.path.join(projectPath, 'webui', 'static', 'uploads', 'images')
        image = cv2.imread(filePath, cv2.IMREAD_UNCHANGED)
        channels = init.channels(image)
        for channel in channels:
            # Pickle each channel image
    
    # Calculam R, G, B
    # Calculam paddedImage R, G, B
    # FFT pentru paddedImage R, G, B
    # Serializare fiecare
    return make_response(jsonify('Initialisations finished!'), 200)
