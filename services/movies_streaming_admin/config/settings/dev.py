import os

from .base import *

DEBUG = True

AWS_S3_HOST = os.environ.get('MINIO_HOST', 'minio')
AWS_S3_PORT = os.environ.get('MINIO_PORT', '9000')
AWS_S3_ENDPOINT_URL = 'http://{host}:{port}'.format(host=AWS_S3_HOST, port=AWS_S3_PORT)
AWS_S3_USE_SSL = False
