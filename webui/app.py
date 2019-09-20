"""
Created on Wed Jan 23 21:20:15 2019

@author: Bogdan
"""
import os

from flask import Flask
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template
from modules.test.controllers import test_mod
from modules.uploads.controllers import UPLOAD_MOD
from modules.initialisations.controllers import INIT_MOD
from modules.processing.controllers import PROCESSING_MOD
from modules.cleanup.controllers import CLEANUP_MOD


# Paths management
APP_ROOT = os.path.dirname(os.path.abspath(__name__))
IMAGES_UPLOAD_DIRECTORY = os.path.join('static', 'uploads', 'images')
VIDEOS_UPLOAD_DIRECTORY = os.path.join('static', 'uploads', 'videos')
EXTRA_IMAGES_UPLOAD_DIRECTORY = os.path.join(IMAGES_UPLOAD_DIRECTORY, 'extra_inputs')
TEMP_DATA_DIRECTORY = os.path.join('static', 'tempdata')

# Application instantiation and configuration
APP = Flask(__name__)
APP.config['IMAGES_DIR'] = os.path.join(APP_ROOT, IMAGES_UPLOAD_DIRECTORY)
APP.config['VIDEOS_DIR'] = os.path.join(APP_ROOT, VIDEOS_UPLOAD_DIRECTORY)
APP.config['EXTRA_IMAGES_DIR'] = os.path.join(APP_ROOT, EXTRA_IMAGES_UPLOAD_DIRECTORY)
APP.config['TEMP_DATA'] = os.path.join(APP_ROOT, TEMP_DATA_DIRECTORY)
APP.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Blueprints Registration
APP.register_blueprint(test_mod)
APP.register_blueprint(UPLOAD_MOD)
APP.register_blueprint(INIT_MOD)
APP.register_blueprint(PROCESSING_MOD)
APP.register_blueprint(CLEANUP_MOD)

# Error handling
@APP.errorhandler(413)
def file_too_large(err):
    return make_response(jsonify('File too big'), 413)

# Binding routes
@APP.route('/')
def index():
    return make_response(render_template('index.html'), 200)

# Run the application
if __name__ == '__main__':
    APP.run(host='localhost', port=8080, debug=True)
