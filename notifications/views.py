from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Holiday, Announcement
from .serializers import (
    HolidaySerializer,
    AnnouncementSerializer,
)
from accounts.permissions import IsAdmin


# =========================================================
# HOLIDAYS
# =========================================================

class HolidayListCreateView(generics.ListCreateAPIView):
    serializer_class = HolidaySerializer

    def get_queryset(self):
        return Holiday.objects.select_related(
            "created_by"
        ).all()

    def get_permissions(self):
        # Everyone authenticated can view holidays
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        # Only Admin can create holidays
        return [IsAdmin()]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


# =========================================================
# HOLIDAY DETAIL
# =========================================================

class HolidayDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = HolidaySerializer

    def get_queryset(self):
        return Holiday.objects.select_related(
            "created_by"
        ).all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdmin()]

    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


# =========================================================
# ANNOUNCEMENTS
# =========================================================

class AnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Announcement.objects.select_related(
            "created_by"
        ).all()

        if user.role == "ADMIN":
            return queryset

        if user.role == "FACULTY":
            return queryset.filter(
                audience__in=["ALL", "FACULTY"]
            )

        if user.role == "STUDENT":
            return queryset.filter(
                audience__in=["ALL", "STUDENT"]
            )

        if user.role == "PLACEMENT":
            return queryset.filter(
                audience__in=["ALL", "PLACEMENT"]
            )

        return Announcement.objects.none()

    def get_permissions(self):
        # Everyone authenticated can view
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        # Only Admin can create
        return [IsAdmin()]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


# =========================================================
# ANNOUNCEMENT DETAIL
# =========================================================

class AnnouncementDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Announcement.objects.select_related(
            "created_by"
        ).all()

        if user.role == "ADMIN":
            return queryset

        if user.role == "FACULTY":
            return queryset.filter(
                audience__in=["ALL", "FACULTY"]
            )

        if user.role == "STUDENT":
            return queryset.filter(
                audience__in=["ALL", "STUDENT"]
            )

        if user.role == "PLACEMENT":
            return queryset.filter(
                audience__in=["ALL", "PLACEMENT"]
            )

        return Announcement.objects.none()

    def get_permissions(self):
        # Everyone authenticated can view
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        # Only Admin can update/delete
        return [IsAdmin()]

    def perform_update(self, serializer):
        serializer.save(
            created_by=self.request.user
        )

