import random
import uuid

from faker import Faker

fake = Faker()
Faker.seed(0)

USERS_COUNT = 500_000
MOVIES_COUNT = 20_000

MOVIES_PER_USER = 20
BOOKMARKS_PER_USER = 50

MAX_RATING = 10
MIN_RATING = 1
MAX_RATINGS_PER_MOVIE = 100
MAX_REVIEWS_PER_MOVIE = 20
MAX_REVIEW_RATINGS_QTY = 20


def get_uuid():
    return str(uuid.uuid4())


def get_random_date():
    return fake.date_time_between(start_date='-3y', end_date='now')


user_ids = [get_uuid() for _ in range(USERS_COUNT)]
movie_ids = [get_uuid() for _ in range(MOVIES_COUNT)]


def generate_user_documents():
    for user_id in user_ids:
        yield {
            '_id': user_id,
            'bookmarks': [
                movie_id for movie_id
                in random.sample(movie_ids, BOOKMARKS_PER_USER)
            ]
        }


def _generate_movie_ratings(movie_id: str):
    ratings_qty = random.randint(1, MAX_RATINGS_PER_MOVIE)
    ratings_sum = 0
    ratings = []
    rating_authors_ids = random.sample(user_ids, ratings_qty)

    for user_id in rating_authors_ids:
        score = random.randint(MIN_RATING, MAX_RATING)
        rating_data = {
            '_id': get_uuid(),
            'user_id': user_id,
            'movie_id': movie_id,
            'score': score,
        }
        ratings.append(rating_data)
        ratings_sum += score
    return ratings, ratings_qty, ratings_sum


def _generate_reviews(movie_id, movie_ratings):
    reviews = []
    reviews_qty = random.randint(1, min(MAX_REVIEWS_PER_MOVIE, len(movie_ratings)))
    related_movie_ratings = random.sample(movie_ratings, reviews_qty)
    for rating_data in related_movie_ratings:
        rating_id = rating_data.get('_id')
        rating_score = rating_data.get('score')
        author_id = rating_data.get('user_id')
        review_rating_qty = random.randint(1, MAX_REVIEW_RATINGS_QTY)
        review_rating_sum = sum(
            random.randint(MIN_RATING, MAX_RATING) for _ in range(review_rating_qty)
        )

        review_data = {
            '_id': get_uuid(),
            'author_id': author_id,
            'movie_id': movie_id,
            'pub_date': get_random_date(),
            'text': f'Test review for {movie_id} by {author_id}',
            'movie_rating_id': rating_id,
            'movie_rating_score': rating_score,
            'review_rating_qty': review_rating_qty,
            'review_rating_sum': review_rating_sum
        }
        reviews.append(review_data)

    return reviews


def generate_movie_and_related_documents(movie_id):
    ratings_docs = []
    ratings, ratings_qty, ratings_sum = _generate_movie_ratings(movie_id)
    reviews = _generate_reviews(movie_id, ratings)
    ratings_docs.extend(ratings)
    movie_doc = {
        '_id': movie_id,
        'ratings_qty': ratings_qty,
        'ratings_sum': ratings_sum,
        'reviews': [review.get('_id') for review in reviews]
    }
    return movie_doc, ratings, reviews
