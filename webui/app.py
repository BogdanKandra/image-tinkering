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
from modules.uploads.controllers import upload_mod
from modules.initialisations.controllers import init_mod
from modules.processing.controllers import processing_mod
from modules.cleanup.controllers import cleanup_mod


# Paths management
APP_ROOT = os.path.dirname(os.path.abspath(__name__))
IMAGES_UPLOAD_DIRECTORY = os.path.join('static', 'uploads', 'images')
VIDEOS_UPLOAD_DIRECTORY = os.path.join('static', 'uploads', 'videos')
EXTRA_IMAGES_UPLOAD_DIRECTORY = os.path.join(IMAGES_UPLOAD_DIRECTORY, 'extra_inputs')
TEMP_DATA_DIRECTORY = os.path.join('static', 'tempdata')

# Application instantiation and configuration
app = Flask(__name__)
app.config['IMAGES_DIR'] = os.path.join(APP_ROOT, IMAGES_UPLOAD_DIRECTORY)
app.config['VIDEOS_DIR'] = os.path.join(APP_ROOT, VIDEOS_UPLOAD_DIRECTORY)
app.config['EXTRA_IMAGES_DIR'] = os.path.join(APP_ROOT, EXTRA_IMAGES_UPLOAD_DIRECTORY)
app.config['TEMP_DATA'] = os.path.join(APP_ROOT, TEMP_DATA_DIRECTORY)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Blueprints Registration
app.register_blueprint(test_mod)
app.register_blueprint(upload_mod)
app.register_blueprint(init_mod)
app.register_blueprint(processing_mod)
app.register_blueprint(cleanup_mod)

# Error handling
@app.errorhandler(413)
def file_too_large(err):
    return make_response(jsonify('File too big'), 413)

# Binding routes
@app.route('/')
def index():
    return make_response(render_template('index.html'), 200)

# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
