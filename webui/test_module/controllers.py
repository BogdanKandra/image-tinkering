"""
Created on Sun Mar 10 12:05:28 2019

@author: Bogdan
"""

from flask.blueprints import Blueprint
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template

test_mod = Blueprint('test', __name__, url_prefix='/test')

@test_mod.route('/', methods=['GET'])
def testing():
    return make_response(jsonify('Pagina home a modulului \'test\''), 200)

@test_mod.route('/operation/<name>', methods=['GET'])
def operation(name):
    return make_response(render_template('test/test_module_index.html', numele=name.capitalize()), 200)
