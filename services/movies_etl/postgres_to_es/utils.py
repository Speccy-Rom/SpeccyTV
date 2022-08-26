import time
from functools import wraps


def backoff(exceptions, logger, total_tries=5, start_sleep_time=1, backoff_factor=2):
    def retry_decorator(func):
        @wraps(func)
        def func_with_retry(*args, **kwargs):
            _try, _delay = 1, start_sleep_time
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if _try >= total_tries:
                        logger.exception('Retry: %d/%d', _try, total_tries)
                        raise
                    logger.exception('Retry: %d/%d. Retrying in %d seconds...', _try, total_tries, _delay)
                    time.sleep(_delay)
                    _try, _delay = _try + 1, _delay * backoff_factor

        return func_with_retry

    return retry_decorator


def coroutine(func):
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner
