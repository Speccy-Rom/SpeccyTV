from datetime import timedelta
from functools import wraps

from core.redis import redis_db


DEFAULT_EXPIRATION_TIME = timedelta(minutes=60)


def delete_items(match):
    cursor = '0'
    while cursor != 0:
        pipe = redis_db.pipeline()
        cursor, keys = redis_db.scan(cursor=cursor, match=match, count=5000)
        for key in keys:
            pipe.delete(key)
        pipe.execute()


def cache_invalidate_group(suffix: str):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            delete_items(match='*_'+suffix)
            return fn(*args, **kwargs)

        return decorator

    return wrapper
