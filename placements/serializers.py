from rest_framework import serializers

from .models import (
    Company,
    PlacementDrive,
    JobApplication,
)


# =========================================================
# COMPANY SERIALIZER
# =========================================================

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company

        fields = [
            "id",
            "company_name",
            "industry",
            "website",
            "hr_name",
            "hr_email",
            "hr_phone",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


# =========================================================
# PLACEMENT DRIVE SERIALIZER
# =========================================================

class PlacementDriveSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PlacementDrive

        fields = [
            "id",
            "company",
            "company_name",
            "job_title",
            "description",
            "package",
            "location",
            "minimum_cgpa",
            "allowed_departments",
            "maximum_backlogs",
            "application_deadline",
            "drive_date",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "company_name",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

    def get_created_by_name(self, obj):
        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )


# =========================================================
# JOB APPLICATION SERIALIZER
# =========================================================

class JobApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_id = serializers.CharField(
        source="student.student_id",
        read_only=True,
    )

    student_department = serializers.CharField(
        source="student.department.name",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="placement_drive.company.company_name",
        read_only=True,
    )

    job_title = serializers.CharField(
        source="placement_drive.job_title",
        read_only=True,
    )

    application_date = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        model = JobApplication

        fields = [
            "id",
            "student",
            "student_id",
            "student_name",
            "student_department",
            "placement_drive",
            "company_name",
            "job_title",
            "resume",
            "status",
            "application_date",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student",
            "student_id",
            "student_name",
            "student_department",
            "company_name",
            "job_title",
            "status",
            "application_date",
            "updated_at",
        ]

    def get_student_name(self, obj):
        return (
            obj.student.user.get_full_name()
            or obj.student.user.username
        )