from datetime import timedelta
from functools import wraps

from core.redis import redis_db

DEFAULT_EXPIRATION_TIME = timedelta(minutes=60)


def delete_items(match):
    for key in redis_db.scan_iter(match=match, count=5000):
        redis_db.delete(key)


def cache_invalidate_group(suffix: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            delete_items(match=f'*_{suffix}')
            return fn(*args, **kwargs)

        return wrapper

    return decorator
