from django.urls import path
from .views import UserAddressView

urlpatterns = [
    path("address/", UserAddressView.as_view(), name="address-list-create"),
    path("address/<int:address_id>/", UserAddressView.as_view(), name="address-detail"),
]
