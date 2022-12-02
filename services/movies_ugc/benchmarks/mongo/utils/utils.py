import time
from functools import wraps

from mongo.config import BENCHMARK_ITERATIONS


def get_random_user_id(db):
    return db.get_collection('users').aggregate([{'$sample': {'size': 1}}]).next().get('_id')


def get_random_movie_id(db):
    return db.get_collection('movies').aggregate([{'$sample': {'size': 1}}]).next().get('_id')


def timer(iterations: int = BENCHMARK_ITERATIONS):
    def decorator(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            run_times = []
            result = None
            for _ in range(iterations):
                start_time = time.perf_counter()
                result = fn(*args, **kwargs)
                end_time = time.perf_counter()
                run_times.append(end_time - start_time)

            avg_time = sum(run_times) / len(run_times)

            print(f'Average execution time for {fn.__name__} (over {iterations} runs): {avg_time:.4f} seconds')
            print(f'Execution result:\n {result}\n')

        return inner

    return decorator
