"""
Created on Sun Mar 10 14:33:41 2019

@author: Bogdan
"""

from flask.blueprints import Blueprint
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template

init_mod = Blueprint('initialisations', __name__, url_prefix='/initialisations')

@init_mod.route('/fourier', methods=['POST'])
def met():
    pass
