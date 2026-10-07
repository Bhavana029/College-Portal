from django.urls import path

from .views import (
    HolidayListCreateView,
    HolidayDetailView,
    AnnouncementListCreateView,
    AnnouncementDetailView,
)


urlpatterns = [
    # =====================================================
    # HOLIDAYS
    # =====================================================

    path(
        "holidays/",
        HolidayListCreateView.as_view(),
        name="holiday-list-create",
    ),

    path(
        "holidays/<int:pk>/",
        HolidayDetailView.as_view(),
        name="holiday-detail",
    ),

    # =====================================================
    # ANNOUNCEMENTS
    # =====================================================

    path(
        "announcements/",
        AnnouncementListCreateView.as_view(),
        name="announcement-list-create",
    ),

    path(
        "announcements/<int:pk>/",
        AnnouncementDetailView.as_view(),
        name="announcement-detail",
    ),
]