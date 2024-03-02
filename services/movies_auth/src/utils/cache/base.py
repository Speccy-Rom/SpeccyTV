import json
from datetime import timedelta
from functools import wraps
from core.redis import redis_db

import models.users

# Default expiration time for cache
DEFAULT_EXPIRATION_TIME = timedelta(minutes=60)


def cache(key_suffix: str, expires: timedelta = DEFAULT_EXPIRATION_TIME):
    """
    Decorator for caching the result of a function.

    Args:
        key_suffix (str): Suffix for the cache key.
        expires (timedelta, optional): Expiration time for the cache. Defaults to DEFAULT_EXPIRATION_TIME.

    Returns:
        function: Decorated function.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(user_id, *args, **kwargs):
            key = f'{user_id}_{key_suffix}'
            item = redis_db.get(key)
            if not item:
                item = fn(user_id, *args, **kwargs)
                redis_db.setex(key, expires, json.dumps(item))
            else:
                item = json.loads(item.decode('utf-8'))
            return item

        return decorator

    return wrapper


def cache_invalidate(key_suffix: str):
    """
    Decorator for invalidating a cache entry.

    Args:
        key_suffix (str): Suffix for the cache key.

    Returns:
        function: Decorated function.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(user_id, *args, **kwargs):
            key = f'{user_id}_{key_suffix}'
            redis_db.delete(key)
            return fn(user_id, *args, **kwargs)

        return decorator

    return wrapper
