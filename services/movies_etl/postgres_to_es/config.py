import os

# ETL
ETL_MODE = os.environ.get('ETL_MODE')
ETL_CHUNK_SIZE = int(os.environ.get('ETL_CHUNK_SIZE'))
ETL_SYNC_DELAY = int(os.environ.get('ETL_SYNC_DELAY'))
ETL_FILE_STATE = os.environ.get('ETL_FILE_STATE')
ETL_DEFAULT_DATE = os.environ.get('ETL_DEFAULT_DATE')

# Postgres
POSTGRES_NAME = os.environ.get('POSTGRES_NAME')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')

# Elasticsearch
ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST')
ELASTICSEARCH_PORT = os.environ.get('ELASTICSEARCH_PORT')
