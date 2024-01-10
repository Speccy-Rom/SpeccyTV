from .base import *  # noqa: F403

DEBUG = True

AWS_S3_HOST = os.environ.get('MINIO_HOST', 'minio')  # noqa: F405
AWS_S3_PORT = os.environ.get('MINIO_PORT', '9000')  # noqa: F405
AWS_S3_ENDPOINT_URL = 'https://{host}:{port}'.format(host=AWS_S3_HOST, port=AWS_S3_PORT)
AWS_S3_USE_SSL = False
