from django.conf import settings
from django.db import models


# =========================================================
# HOLIDAY
# =========================================================

class Holiday(models.Model):

    title = models.CharField(
        max_length=150
    )

    date = models.DateField()

    description = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="holidays_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.title} - {self.date}"


# =========================================================
# ANNOUNCEMENT
# =========================================================

class Announcement(models.Model):

    AUDIENCE_CHOICES = (
        ("ALL", "Everyone"),
        ("STUDENT", "Students"),
        ("FACULTY", "Faculty"),
        ("PLACEMENT", "Placement Cell"),
    )

    TYPE_CHOICES = (
        ("GENERAL", "General Announcement"),
        ("EXAM", "Exam Dates"),
        ("IMPORTANT", "Important Notice"),
    )

    title = models.CharField(
        max_length=200
    )

    notice_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="GENERAL",
    )

    description = models.TextField()

    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default="ALL",
    )

    event_date = models.DateField(
        blank=True,
        null=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="announcements_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title