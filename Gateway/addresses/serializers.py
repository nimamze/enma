from rest_framework import serializers
from .models import UserAddresses


class AddUserAddressesSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=True)
    longitude = serializers.FloatField(write_only=True, required=True)

    class Meta:
        model = UserAddresses
        fields = [
            "latitude",
            "longitude",
            "title",
            "province",
            "city",
            "street",
            "alley",
            "plaque",
            "unit",
            "postal_code",
        ]


class UpdateUserAddressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddresses
        fields = [
            "is_default",
            "title",
            "street",
            "alley",
            "plaque",
            "unit",
            "postal_code",
        ]


class DisplayUserAddressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddresses
        fields = [
            "id",
            "is_default",
            "title",
            "province",
            "city",
            "street",
            "alley",
            "plaque",
            "unit",
            "postal_code",
        ]
