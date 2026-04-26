from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.core.exceptions import ValidationError
from core.models import SoftDeleteModel
import uuid
from django.conf import settings
from core.utils.storage_backends import UsersMediaStorage
from core.utils.tasks import delete_user_avatar_task

if not settings.SAVE_FILES_LOCALLY:
    users_storage = UsersMediaStorage()
else:
    users_storage = None


class UserDeletionBackup(models.Model):
    user = models.OneToOneField(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="deletion_backup",
    )
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backup for {self.user_id}"  # type: ignore


class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Phone is required")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=phone,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, phone, password, **extra_fields)


class CustomUser(AbstractUser, SoftDeleteModel):
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=16, db_index=True)

    image = models.ImageField(
        upload_to="users/avatars/",
        storage=users_storage if users_storage else None,
        null=True,
        blank=True,
    )
    is_seller = models.BooleanField(default=False)
    username = None
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
    objects = UserManager()  # type: ignore

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        avatar_name = self.image.name if self.image else None

        UserDeletionBackup.objects.update_or_create(
            user=self,
            defaults={"email": self.email, "phone": self.phone},
        )

        unique_suffix = uuid.uuid4().hex
        self.email = f"deleted__{unique_suffix}@deleted.local"
        self.phone = f"deleted__{unique_suffix}"
        self.is_deleted = True
        self.image = None

        self.save(update_fields=["email", "phone", "is_deleted", "image"])

        if avatar_name:
            transaction.on_commit(lambda: delete_user_avatar_task.delay(avatar_name))  # type: ignore

    @transaction.atomic
    def restore(self, new_email=None, new_phone=None):
        if not self.is_deleted:
            raise ValidationError("User is not deleted.")
        try:
            backup = self.deletion_backup  # type: ignore
        except UserDeletionBackup.DoesNotExist:
            raise ValidationError("No backup exists for this user.")
        target_email = backup.email
        email_conflict = (
            CustomUser.objects.filter(
                email=target_email,
                is_deleted=False,
            )
            .exclude(id=self.id)  # type: ignore
            .exists()
        )
        if email_conflict:
            if not new_email:
                raise ValidationError(
                    "Original email is already in use. Provide a new email."
                )
            if CustomUser.objects.filter(
                email=new_email,
                is_deleted=False,
            ).exists():
                raise ValidationError("New email is already in use.")
            target_email = new_email
        target_phone = backup.phone
        phone_conflict = (
            CustomUser.objects.filter(
                phone=target_phone,
                is_deleted=False,
            )
            .exclude(id=self.id)  # type: ignore
            .exists()
        )
        if phone_conflict:
            if not new_phone:
                raise ValidationError(
                    "Original phone is already in use. Provide a new phone."
                )
            if CustomUser.objects.filter(
                phone=new_phone,
                is_deleted=False,
            ).exists():
                raise ValidationError("New phone is already in use.")
            target_phone = new_phone
        self.email = target_email
        self.phone = target_phone
        self.is_deleted = False
        self.save(update_fields=["email", "phone", "is_deleted"])
        backup.delete()

    def __str__(self):
        return f"{self.get_full_name().strip()} - {self.phone}"
