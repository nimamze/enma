from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    AddUserAddressesSerializer,
    UpdateUserAddressesSerializer,
    DisplayUserAddressesSerializer,
)
from django.contrib.auth import get_user_model
from .models import UserAddresses
from utils.map import reverse_geocode, MapIrError
from django.conf import settings

User = get_user_model()


class UserAddressView(APIView):
    @swagger_auto_schema(security=[{"Bearer": []}])
    def get(self, request, address_id=None):
        user = request.user
        if address_id:
            address = UserAddresses.objects.filter(user=user, id=address_id).first()
            if address is None:
                return Response(
                    {"detail": "address not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = DisplayUserAddressesSerializer(address)

        else:
            addresses = UserAddresses.objects.filter(user=user)
            if not addresses.exists():
                return Response(
                    {"detail": "no addresses"},
                    status=status.HTTP_200_OK,
                )
            serializer = DisplayUserAddressesSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(security=[{"Bearer": []}])
    def post(self, request):
        user = request.user
        address_count = UserAddresses.objects.filter(user=user).count()

        if address_count < settings.USER_MAX_ADDRESSES:
            serializer = AddUserAddressesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            latitude = data["latitude"]  # type: ignore
            longitude = data["longitude"]  # type: ignore
            try:
                result = reverse_geocode(latitude, longitude)
                country = result.get("country")
                if country != "ایران":
                    return Response(
                        {"detail": "address must be in iran country"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                province = result.get("province")
                city = result.get("city")
                street = result.get("street")
                alley = result.get("alley")
            except MapIrError:
                province = data.get("province")  # type: ignore
                city = data.get("city")  # type: ignore
                street = data.get("street")  # type: ignore
                alley = data.get("alley")  # type: ignore
            address = UserAddresses(
                user=user,
                latitude=latitude,
                longitude=longitude,
                title=data.get("title"),  # type: ignore
                province=province,
                city=city,
                street=street,
                alley=alley,
                plaque=data["plaque"],  # type: ignore
                unit=data.get("unit"),  # type: ignore
                postal_code=data["postal_code"],  # type: ignore
            )
            address.save()
            return Response(
                {"detail": "address added successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"detail": "you can't add addresses anymore"},
                status=status.HTTP_403_FORBIDDEN,
            )

    @swagger_auto_schema(security=[{"Bearer": []}])
    def put(self, request, address_id):
        user = request.user
        address = UserAddresses.objects.filter(user=user, id=address_id).first()
        if address is None:
            return Response(
                {"detail": "address not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UpdateUserAddressesSerializer(
            address, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        is_default = data.get("is_default")  # type: ignore
        if is_default is True:
            previous_default_address = UserAddresses.objects.filter(
                user=user, is_default=True
            ).first()
            if previous_default_address is not None:
                previous_default_address.is_default = False  # type: ignore
                previous_default_address.save()  # type: ignore
        serializer.save()
        return Response(
            {"detail": "address updated successfully"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(security=[{"Bearer": []}])
    def delete(self, request, address_id):
        user = request.user
        address = UserAddresses.objects.filter(user=user, id=address_id).first()
        if address is None:
            return Response(
                {"detail": "address not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
