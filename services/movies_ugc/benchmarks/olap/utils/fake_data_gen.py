import random
import uuid
from collections import namedtuple
from datetime import timedelta

NUMBER_OF_MOVIES = 10_000
MIN_MOVIE_DURATION = int(timedelta(minutes=15).total_seconds())
MAX_MOVIE_DURATION = int(timedelta(hours=4, minutes=30).total_seconds())
MAX_MOVIES_PER_USER = 100

Movie = namedtuple('Movie', ['id', 'duration'])
Row = namedtuple('Row', ['user_id', 'movie_id', 'viewed_frame'])

movies = [
    Movie(uuid.uuid4(), random.randint(MIN_MOVIE_DURATION, MAX_MOVIE_DURATION))
    for _ in range(NUMBER_OF_MOVIES)
]


def generate_fake_data(
    batch_size: int,
    num_of_batches: int
):
    return (generate_batch(batch_size) for _ in range(num_of_batches))


def generate_batch(size: int):
    counter = 0
    batch = []
    while counter < size:
        movies_per_user = random.sample(
            movies,
            random.randint(1, MAX_MOVIES_PER_USER)
        )
        user_id = uuid.uuid4()
        for movie in movies_per_user:
            batch.append(
                Row(user_id, movie.id, random.randint(1, movie.duration))
            )
            counter += 1

    if len(batch) > size:
        batch = batch[:size]
    return batch
