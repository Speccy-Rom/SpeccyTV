from flask import Flask
from authlib.integrations.flask_client import OAuth

from core import config

oauth = OAuth()


def init_oauth(app: Flask):
    oauth.init_app(app)
    oauth.register(**config.OAUTH['Google'])
