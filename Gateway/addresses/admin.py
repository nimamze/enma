from django.contrib import admin
from .models import UserAddresses


@admin.register(UserAddresses)
class UserAddressesAdmin(admin.ModelAdmin):
    list_display = (
        "get_user_full_name",
        "get_user_phone",
        "city",
        "street",
        "is_default",
    )
    list_filter = ("is_default", "city", "province")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__phone",
        "city",
        "street",
        "alley",
        "plaque",
        "title",
        "postal_code",
    )
    ordering = ("-city",)

    def get_user_full_name(self, obj):
        full_name = obj.user.get_full_name().strip()
        return full_name or f"User #{obj.user.id}"

    def get_user_phone(self, obj):
        return obj.user.phone

    get_user_full_name.short_description = "Full name"
    get_user_phone.short_description = "Phone"
    get_user_full_name.admin_order_field = "user__last_name"
