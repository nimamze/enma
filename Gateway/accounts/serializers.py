from rest_framework import serializers
from django.contrib.auth import get_user_model
import phonenumbers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


def phoneValidation(phone):
    try:
        phone = phonenumbers.parse(phone, "IR")
        if not phonenumbers.is_valid_number(phone):
            raise serializers.ValidationError("Invalid Iranian phone number")
        if phonenumbers.region_code_for_number(phone) != "IR":
            raise serializers.ValidationError("Phone must belong to Iran")
        phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        return phone
    except phonenumbers.NumberParseException:
        raise serializers.ValidationError("Invalid phone format")


class SignUpSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "phone",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "password_confirm": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def validate(self, data):
        password = data.get("password")
        validate_password(password)
        password_confirm = data.get("password_confirm")
        if password != password_confirm:
            raise serializers.ValidationError(
                "password and password_confirm are not same as each other!"
            )
        phone = data.get("phone")
        data["phone"] = phoneValidation(phone)
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "image", "phone", "email"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "image", "email"]


class SendOtpSerializer(serializers.Serializer):
    user_email = serializers.EmailField(required=False, allow_blank=True)
    user_phone = serializers.CharField(required=False, allow_blank=True)
    send_way = serializers.ChoiceField(choices=[("sms", "sms"), ("email", "email")])
    purpose = serializers.ChoiceField(
        choices=[
            ("sign_up", "sign_up"),
            ("become_seller", "become_seller"),
            ("phone_change", "phone_change"),
            ("password_change", "password_change"),
            ("password_forget", "password_forget"),
        ]
    )

    def validate(self, data):
        send_way = data["send_way"]
        if send_way == "sms":
            if not data.get("user_phone"):
                raise serializers.ValidationError("Phone required for sms")
            data["user_phone"] = phoneValidation(data["user_phone"])
        else:
            if not data.get("user_email"):
                raise serializers.ValidationError("Email required for email")
        return data


class VerifyOtpSerializer(serializers.Serializer):
    validation_otp = serializers.CharField(max_length=6)
    user_phone = serializers.CharField(required=False, allow_blank=True)
    purpose = serializers.ChoiceField(choices=[...])

    def validate(self, data):
        request = self.context.get("request")
        if not request.user.is_authenticated:  # type: ignore
            if not data.get("user_phone"):
                raise serializers.ValidationError("phone required for verify")
            data["user_phone"] = phoneValidation(data["user_phone"])
        return data


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    new_confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        new_password = data.get("new_password")
        validate_password(new_password)
        new_confirm_password = data.get("new_confirm_password")
        if new_password != new_confirm_password:
            raise serializers.ValidationError(
                "password and password_confirm are not same as each other!"
            )
        return data


class PhoneChangeSerializer(serializers.Serializer):
    previous_phone = serializers.CharField(max_length=16, required=True)
    new_phone = serializers.CharField(max_length=16, required=True)

    def validate(self, data):
        new_phone = data.get("new_phone")
        data["new_phone"] = phoneValidation(new_phone)
        previous_phone = data.get("previous_phone")
        data["previous_phone"] = phoneValidation(previous_phone)
        return data
