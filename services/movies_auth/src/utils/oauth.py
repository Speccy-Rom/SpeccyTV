from flask import Flask
from authlib.integrations.flask_client import OAuth

from core import config

oauth = OAuth()


def init_oauth(app: Flask):
    """
    Initialize the OAuth client with the application's configuration.

    This function sets up the OAuth client by initializing it with the Flask application
    and registering a new OAuth client named 'Google'. The details for this client are
    coming from the `config.OAUTH['Google']` dictionary.

    Args:
        app (Flask): The Flask application to initialize the OAuth client for.

    """
    oauth.init_app(app)
    oauth.register(**config.OAUTH['Google'])
