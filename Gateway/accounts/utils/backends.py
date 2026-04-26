from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthentication(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        phone = username or kwargs.get("phone")
        if phone is None or password is None:
            return None
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
