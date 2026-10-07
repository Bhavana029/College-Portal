from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom Django Admin configuration
    for our User model.
    """

    # Fields shown in the user list
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "phone",
        "is_active",
    )

    # Filters on the right side
    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )

    # Search fields
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    # Fields displayed while editing a user
    fieldsets = UserAdmin.fieldsets + (
        (
            "College Portal Information",
            {
                "fields": (
                    "role",
                    "phone",
                )
            },
        ),
    )

    # Fields displayed when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "College Portal Information",
            {
                "fields": (
                    "role",
                    "phone",
                )
            },
        ),
    )