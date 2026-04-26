from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .tasks import send_email_task

User = get_user_model()


@receiver(post_save, sender=User, dispatch_uid="user_created_signal")
def userCreatedHandler(sender, instance, created, **kwargs):
    if created:
        send_email_task(instance.email, "Welcome to our site!")


@receiver(post_delete, sender=User, dispatch_uid="user_deleted_signal")
def userDeletedHandler(sender, instance, **kwargs):
    send_email_task(
        instance.email, "Sorry to hear you are leaving us, wish you the best!"
    )
