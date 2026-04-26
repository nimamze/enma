from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .utils.forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("get_user_fullname", "phone", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_seller")
    search_fields = ("phone", "email", "first_name", "last_name")
    ordering = ("last_name",)
    readonly_fields = ("created_at", "updated_at")
    add_fieldsets = (
        (
            "Personal Informations",
            {"fields": ("phone", "email", "password1", "password2")},
        ),
    )
    fieldsets = (
        (
            "Personal Informations",
            {
                "fields": (
                    "phone",
                    "email",
                    "first_name",
                    "last_name",
                    "image",
                    "is_seller",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )

    @admin.display(description="Full Name")
    def get_user_fullname(self, obj):
        return obj.get_full_name()


admin.site.register(CustomUser, CustomUserAdmin)
