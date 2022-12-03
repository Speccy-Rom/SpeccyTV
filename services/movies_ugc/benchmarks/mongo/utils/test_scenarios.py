import pymongo
from pymongo import MongoClient

from mongo import config as cfg
from mongo.utils.test_data_gen import get_random_date, get_uuid
from mongo.utils.utils import get_random_movie_id, get_random_user_id, timer

client = MongoClient(cfg.MONGO_HOST, cfg.MONGO_PORT)
db = client.get_database(cfg.DB_NAME)

MOVIE_RATINGS = db.get_collection('movie_ratings')
USERS = db.get_collection('users')
MOVIES = db.get_collection('movies')
REVIEWS = db.get_collection('reviews')


@timer()
def get_movie_reviews_sort_pub_date(movie_id):
    reviews = REVIEWS.find({'movie_id': movie_id}).sort('pub_date', pymongo.DESCENDING)
    return list(reviews)


@timer()
def get_movie_reviews_sort_movie_rating(movie_id):
    reviews = REVIEWS.find({'movie_id': movie_id}).sort('movie_rating_score', pymongo.DESCENDING)
    return list(reviews)


@timer()
def get_users_liked_movies(user_id, rating_threshold=1):
    good_ratings = MOVIE_RATINGS.find({'user_id': user_id, 'score': {'$gte': rating_threshold}})
    return [rating.get('movie_id') for rating in good_ratings]


@timer()
def get_movie_ratings_count(movie_id):
    movie = MOVIES.find_one({'_id': movie_id})
    return movie.get('ratings_qty')


@timer()
def get_movie_good_ratings_count(movie_id, rating_threshold=6):
    good_ratings_count = MOVIE_RATINGS.count_documents(
        {'movie_id': movie_id, 'score': {'$gte': rating_threshold}}
    )
    return good_ratings_count


@timer()
def get_avg_movie_rating(movie_id):
    movie = MOVIES.find_one({'_id': movie_id})

    ratings_sum = movie.get('ratings_sum')
    ratings_qty = movie.get('ratings_qty')

    if ratings_qty > 0:
        return ratings_sum / ratings_qty
    return 'Movie has no ratings yet'


@timer()
def add_movie_rating(movie_id, user_id, score):
    rating_doc = {
        '_id': get_uuid(),
        'user_id': user_id,
        'movie_id': movie_id,
        'score': score,
    }

    rating_id = MOVIE_RATINGS.insert_one(rating_doc).inserted_id

    MOVIES.update_one(
        {'_id': movie_id},
        {'$inc': {'ratings_sum': score, 'ratings_qty': 1}}
    )

    return f'Inserted rating with id: {rating_id}'


@timer()
def add_bookmark(user_id, movie_id):
    USERS.update_one(
        {'_id': user_id},
        {'$addToSet': {'bookmarks': movie_id}}
    )

    return f'Added bookmark for movie: {movie_id} to user: {user_id}'


@timer()
def add_review(user_id, movie_id, score):
    rating_id = get_uuid()
    rating_doc = {
        '_id': rating_id,
        'user_id': user_id,
        'movie_id': movie_id,
        'score': score,
    }

    review_doc = {
        '_id': get_uuid(),
        'author_id': user_id,
        'movie_id': movie_id,
        'pub_date': get_random_date(),
        'text': f'Test review for {movie_id} by {user_id}',
        'movie_rating_id': rating_id,
        'movie_rating_score': score,
        'review_rating_qty': 10,
        'review_rating_sum': 45
    }

    MOVIE_RATINGS.insert_one(rating_doc)

    MOVIES.update_one(
        {'_id': movie_id},
        {'$inc': {'ratings_sum': score, 'ratings_qty': 1}}
    )
    review_id = REVIEWS.insert_one(review_doc).inserted_id

    return f'Added movie_review with id: {review_id}'


READ_SCENARIOS = [
    {
        'func': get_movie_reviews_sort_pub_date,
        'kwargs': {'movie_id': get_random_movie_id(db)}
    },
    {
        'func': get_movie_reviews_sort_movie_rating,
        'kwargs': {'movie_id': get_random_movie_id(db)}
    },
    {
        'func': get_users_liked_movies,
        'kwargs': {'user_id': get_random_user_id(db)}
    },
    {
        'func': get_movie_ratings_count,
        'kwargs': {'movie_id': get_random_movie_id(db)}
    },
    {
        'func': get_movie_good_ratings_count,
        'kwargs': {'movie_id': get_random_movie_id(db)}
    },
    {
        'func': get_avg_movie_rating,
        'kwargs': {'movie_id': get_random_movie_id(db)}
    },
]

WRITE_SCENARIOS = [
    {
        'func': add_movie_rating,
        'kwargs': {
            'movie_id': get_random_movie_id(db),
            'user_id': get_random_user_id(db),
            'score': 6,
        }
    },
    {
        'func': add_review,
        'kwargs': {
            'movie_id': get_random_movie_id(db),
            'user_id': get_random_user_id(db),
            'score': 6,
        }
    },
    {
        'func': add_bookmark,
        'kwargs': {
            'movie_id': get_random_movie_id(db),
            'user_id': get_random_user_id(db),
        }
    },

]
