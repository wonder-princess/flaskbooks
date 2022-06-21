from flask import Blueprint, Flask, jsonify, request
from flaskbook_api.api import calculation

api = Blueprint("api", __name__)

'''
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    return app
'''
