import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
DOCS_DIR = BASE_DIR.joinpath('docs').joinpath('v1')

DATABASE_URI = 'postgresql://{username}:{password}@{host}:{port}/{database_name}'.format(
    username=os.environ.get('POSTGRES_USER'), password=os.environ.get('POSTGRES_PASSWORD'),
    host=os.environ.get('POSTGRES_AUTH_HOST'), port=os.environ.get('POSTGRES_AUTH_PORT'),
    database_name=os.environ.get('POSTGRES_NAME')
)

REDIS_HOST = os.environ.get('REDIS_AUTH_HOST')
REDIS_PORT = os.environ.get('REDIS_AUTH_PORT')

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

ACCESS_EXPIRES = timedelta(minutes=30)
REFRESH_EXPIRES = timedelta(days=1)

RATELIMIT_DEFAULT = "10/second"
RATELIMIT_STORAGE_URL = "redis://{host}:{port}".format(host=REDIS_HOST, port=REDIS_PORT)
RATELIMIT_HEADERS_ENABLED = True
RATELIMIT_IN_MEMORY_FALLBACK = "1/2second"
RATELIMIT_KEY_PREFIX = "limiter"
RATELIMIT_SWALLOW_ERRORS = True

OAUTH = {
    'Google': {
        'name': 'google',
        'server_metadata_url': 'https://accounts.google.com/.well-known/openid-configuration',
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'client_kwargs': {
            'scope': 'openid email profile'
        }
    }
}

DB_USERS_PARTITIONS_NUM = 8

JAEGER_HOST = os.getenv('JAEGER_HOST')
