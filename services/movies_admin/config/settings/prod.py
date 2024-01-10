from .base import *  # noqa: F403

DEBUG = False

AWS_S3_ENDPOINT_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'  # noqa: F405
AWS_S3_USE_SSL = False
AWS_S3_FILE_OVERWRITE = False
