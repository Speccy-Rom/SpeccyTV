import json
from datetime import timedelta
from functools import wraps
from inspect import getfullargspec

from core.redis import redis_db
import models.users


DEFAULT_EXPIRATION_TIME = timedelta(minutes=60)
USER_ID_ARG_NAME = 'user_id'


def _get_user_id(fn, args, kwargs):
    if user_id := kwargs.get(USER_ID_ARG_NAME):
        return user_id
    if args:
        argspec = getfullargspec(fn)
        try:
            user_id_index = argspec.args.index(USER_ID_ARG_NAME)
            return args[user_id_index]
        except ValueError:
            pass

        self_arg = args[0]
        if type(self_arg) == models.users.User:
            return self_arg.id

    raise RuntimeError("Can't determine user_id")


def cache(key_suffix: str, expires: timedelta = DEFAULT_EXPIRATION_TIME):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = _get_user_id(fn, args, kwargs)
            item = get_item(user_id, key_suffix)
            if not item:
                item = fn(*args, **kwargs)
                set_item(user_id, key_suffix, item, expires)

            return item

        return decorator

    return wrapper


def cache_invalidate(key_suffix: str):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = _get_user_id(fn, args, kwargs)
            delete_item(user_id, key_suffix)
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def _get_key(user_id, key_suffix):
    return '{}_{}'.format(user_id, key_suffix)


def get_item(user_id, key_suffix):
    key = _get_key(user_id, key_suffix)
    if not (res := redis_db.get(key)):
        return None
    res = res.decode('utf-8')
    return json.loads(res)


def set_item(user_id, key_suffix, value, expiration=DEFAULT_EXPIRATION_TIME):
    key = _get_key(user_id, key_suffix)
    value_str = json.dumps(value)
    redis_db.setex(key, expiration, value_str)


def delete_item(user_id, key_suffix):
    key = _get_key(user_id, key_suffix)
    redis_db.delete(key)
