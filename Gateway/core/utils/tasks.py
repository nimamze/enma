from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from .sms import send_sms
import boto3
from botocore.exceptions import ClientError

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, phone, message):
    try:
        send_sms(phone, f"Enma Site:\n{message}")
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, email_address, message):
    try:
        send_mail(
            "Enma Site",
            message,
            settings.EMAIL_HOST_USER,
            [email_address],
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_jwt_tokens():
    call_command("flushexpiredtokens")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_for_not_login_users(self):
    try:
        one_month_ago = timezone.now() - timedelta(days=30)
        inactive_users = User.objects.filter(
            Q(last_login__lt=one_month_ago) | Q(last_login__isnull=True)
        )
        for user in inactive_users:
            send_mail(
                subject="Enma Site",
                message="Check the site — you haven't logged in for one month!",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def delete_user_avatar_task(self, file_name):
    if not file_name:
        return

    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_USERS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_USERS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_USERS_SECRET_ACCESS_KEY,
        )

        s3.delete_object(
            Bucket=settings.AWS_USERS_STORAGE_BUCKET_NAME,
            Key=file_name,
        )

    except ClientError as exc:
        raise self.retry(exc=exc)
