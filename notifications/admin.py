from django.contrib import admin

from .models import (
    Holiday,
    Announcement,
)


# =========================================================
# HOLIDAY
# =========================================================

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "date",
        "created_by",
        "created_at",
    )

    list_filter = (
        "date",
    )

    search_fields = (
        "title",
        "description",
    )

    autocomplete_fields = (
        "created_by",
    )


# =========================================================
# ANNOUNCEMENT
# =========================================================

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "audience",
        "created_by",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "audience",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    autocomplete_fields = (
        "created_by",
    )