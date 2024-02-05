from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr as get_remote_address

from core import config


limiter = Limiter(key_func=get_remote_address)


def init_limiter(app: Flask):
    """
    Initialize the rate limiter with the application's configuration.

    This function sets up the rate limiter by configuring it with the settings
    defined in the application's configuration. The settings include the default
    rate limit, the storage URL for the rate limit data, whether rate limit headers
    are enabled, the in-memory fallback for the rate limit, the key prefix for the
    rate limit, and whether rate limit errors should be swallowed.

    Args:
        app (Flask): The Flask application to initialize the rate limiter for.

    """
    # Set the default rate limit
    app.config["RATELIMIT_DEFAULT"] = config.RATELIMIT_DEFAULT
    # Set the storage URL for the rate limit data
    app.config["RATELIMIT_STORAGE_URL"] = config.RATELIMIT_STORAGE_URL
    # Set whether rate limit headers are enabled
    app.config["RATELIMIT_HEADERS_ENABLED"] = config.RATELIMIT_HEADERS_ENABLED
    # Set the in-memory fallback for the rate limit
    app.config["RATELIMIT_IN_MEMORY_FALLBACK"] = config.RATELIMIT_IN_MEMORY_FALLBACK
    # Set the key prefix for the rate limit
    app.config["RATELIMIT_KEY_PREFIX"] = config.RATELIMIT_KEY_PREFIX
    # Set whether rate limit errors should be swallowed
    app.config["RATELIMIT_SWALLOW_ERRORS"] = config.RATELIMIT_SWALLOW_ERRORS
    # Initialize the rate limiter with the application
    limiter.init_app(app)
