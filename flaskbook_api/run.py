import os

from flask import Flask

from flaskbook_api.api import api
# from flaskbook_api.api import create_app
# from flaskbook_api.api import api, create_app
from flaskbook_api.api.config import config

# app = create_app(config)
config_name = os.environ.get("CONFIG", "local")

app = Flask(__name__)
app.config.from_object(config[config_name])
app.register_blueprint(api)
