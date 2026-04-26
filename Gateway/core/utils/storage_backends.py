from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class UsersMediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_USERS_STORAGE_BUCKET_NAME
    endpoint_url = settings.AWS_USERS_S3_ENDPOINT_URL
    access_key = settings.AWS_USERS_ACCESS_KEY_ID
    secret_key = settings.AWS_USERS_SECRET_ACCESS_KEY
    querystring_auth = False
    default_acl = "public-read"
    file_overwrite = False
