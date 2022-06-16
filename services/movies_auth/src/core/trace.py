from functools import wraps

import opentracing
from jaeger_client import Config

from .config import JAEGER_HOST

CONFIG = {
    'sampler': {
        'type': 'const',
        'param': 1,
    },
    'local_agent': {
        'reporting_host': JAEGER_HOST
    }
}


def setup_jaeger():
    config = Config(
        config=CONFIG,
        service_name='movies_auth',
        validate=True,
    )
    return config.initialize_tracer()


def trace(func):
    @wraps(func)
    def inner(*args, **kwargs):
        from app import tracer
        parent_span = tracer.get_span()
        with opentracing.tracer.start_span(func.__name__, child_of=parent_span):
            return func(*args, **kwargs)

    return inner
