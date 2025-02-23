import time
import logging
from functools import wraps
from typing import Callable, Type, Any, Tuple

def backoff(
    exceptions: Tuple[Type[Exception], ...],
    logger: logging.Logger,
    total_tries: int = 5,
    start_sleep_time: int = 1,
    backoff_factor: int = 2
) -> Callable:
    """
    Retry decorator with exponential backoff.

    Args:
        exceptions (Tuple[Type[Exception], ...]): Exceptions to catch.
        logger (logging.Logger): Logger instance to log retries.
        total_tries (int): Total number of retry attempts.
        start_sleep_time (int): Initial sleep time between retries.
        backoff_factor (int): Factor by which the sleep time increases.

    Returns:
        Callable: Decorated function with retry logic.
    """
    def retry_decorator(func: Callable) -> Callable:
        @wraps(func)
        def func_with_retry(*args: Any, **kwargs: Any) -> Any:
            attempt, delay = 1, start_sleep_time
            while attempt <= total_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == total_tries:
                        logger.exception('Retry: %d/%d failed. Raising exception.', attempt, total_tries)
                        raise
                    logger.exception('Retry: %d/%d failed. Retrying in %d seconds...', attempt, total_tries, delay)
                    time.sleep(delay)
                    attempt += 1
                    delay *= backoff_factor

        return func_with_retry

    return retry_decorator


def coroutine(func: Callable) -> Callable:
    """
    Coroutine decorator to automatically start coroutines.

    Args:
        func (Callable): Coroutine function to decorate.

    Returns:
        Callable: Decorated coroutine function.
    """
    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        coroutine_func = func(*args, **kwargs)
        next(coroutine_func)
        return coroutine_func

    return inner