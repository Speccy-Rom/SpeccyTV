import os

# ETL
ETL_MODE = os.environ.get('ETL_MODE', 'default_mode')
ETL_CHUNK_SIZE = int(os.environ.get('ETL_CHUNK_SIZE', 100))
ETL_SYNC_DELAY = int(os.environ.get('ETL_SYNC_DELAY', 60))
ETL_FILE_STATE = os.environ.get('ETL_FILE_STATE', 'state.json')
ETL_DEFAULT_DATE = os.environ.get('ETL_DEFAULT_DATE', '1970-01-01')

# Postgres
POSTGRES_NAME = os.environ.get('POSTGRES_NAME', 'postgres')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'password')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')

# Elasticsearch
ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = os.environ.get('ELASTICSEARCH_PORT', '9200')