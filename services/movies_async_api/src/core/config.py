import os
from logging import config as logging_config

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = 'Movies Async API v1'

CACHE_EXPIRATION = int(os.getenv('CACHE_EXPIRATION', 60 * 5))

PAGE_SIZE = int(os.getenv('PAGE_SIZE', 50))

TIME_LIMIT = int(os.getenv('TIME_LIMIT', 5))

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

ELASTIC_HOST = os.getenv('ELASTICSEARCH_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
