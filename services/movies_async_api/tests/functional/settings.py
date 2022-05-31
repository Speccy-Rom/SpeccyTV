import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_TEST_DB = 2

ELASTIC_HOST = os.getenv('ELASTICSEARCH_HOST')
ELASTIC_PORT = os.getenv('ELASTICSEARCH_PORT')
ELASTIC_FILM_INDEX = 'movies'
ELASTIC_PERSON_INDEX = 'persons'
ELASTIC_GENRE_INDEX = 'genres'
ELASTIC_FILM_SCHEMA = os.path.join(BASE_DIR, 'test_data/elastic/schemas/movies.json')
ELASTIC_PERSON_SCHEMA = os.path.join(BASE_DIR, 'test_data/elastic/schemas/persons.json')
ELASTIC_GENRE_SCHEMA = os.path.join(BASE_DIR, 'test_data/elastic/schemas/genres.json')
ELASTIC_PERSON_DATA = os.path.join(BASE_DIR, 'test_data/elastic/data/persons.txt')
ELASTIC_FILM_DATA = os.path.join(BASE_DIR, 'test_data/elastic/data/movies.txt')
ELASTIC_GENRE_DATA = os.path.join(BASE_DIR, 'test_data/elastic/data/genres.txt')

API_HOST = os.getenv('API_HOST')
API_PORT = os.getenv('API_PORT')
