from rest_framework import serializers
from .models import Holiday, Announcement


class HolidaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = "__all__"


class AnnouncementSerializer(serializers.ModelSerializer):

    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "notice_type",
            "description",
            "audience",
            "event_date",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_created_by_name(self, obj):
        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )