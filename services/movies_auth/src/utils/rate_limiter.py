from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr as get_remote_address

from core import config


limiter = Limiter(key_func=get_remote_address)


def init_limiter(app: Flask):
    app.config["RATELIMIT_DEFAULT"] = config.RATELIMIT_DEFAULT
    app.config["RATELIMIT_STORAGE_URL"] = config.RATELIMIT_STORAGE_URL
    app.config["RATELIMIT_HEADERS_ENABLED"] = config.RATELIMIT_HEADERS_ENABLED
    app.config["RATELIMIT_IN_MEMORY_FALLBACK"] = config.RATELIMIT_IN_MEMORY_FALLBACK
    app.config["RATELIMIT_KEY_PREFIX"] = config.RATELIMIT_KEY_PREFIX
    app.config["RATELIMIT_SWALLOW_ERRORS"] = config.RATELIMIT_SWALLOW_ERRORS
    limiter.init_app(app)
