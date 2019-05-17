"""
Created on Fri May 17 13:10:30 2019

@author: Bogdan
"""
from flask.blueprints import Blueprint
from flask.globals import request


cleanup_mod = Blueprint('cleanup', __name__, url_prefix='/cleanup')

@cleanup_mod.route('/', methods=['POST'])
def cleanup():
    
    filenames = request.get_json()['filenames']
    
    # Delete processed files (from tempdata)
    # Delete pickles (from tempdata, _b, _g, _r)
    # Delete uploaded files (from uploads/images)
    for filename in filenames:
        