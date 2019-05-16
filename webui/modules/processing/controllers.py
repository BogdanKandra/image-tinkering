"""
Created on Thu May 16 12:29:17 2019

@author: Bogdan
"""
from flask.blueprints import Blueprint


processing_mod = Blueprint('processing', __name__, url_prefix='/process')

@processing_mod.route('/', methods=['POST'])
def process():
    pass
