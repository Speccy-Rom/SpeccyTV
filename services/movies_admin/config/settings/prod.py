from .base import *

DEBUG = False

AWS_S3_ENDPOINT_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_USE_SSL = False
AWS_S3_FILE_OVERWRITE = False
