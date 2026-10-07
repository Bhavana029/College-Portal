from django.contrib import admin

from .models import (
    Company,
    PlacementDrive,
    JobApplication,
)


# =========================================================
# COMPANY
# =========================================================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "company_name",
        "industry",
        "hr_name",
        "hr_email",
        "hr_phone",
        "created_at",
    )

    search_fields = (
        "company_name",
        "industry",
        "hr_name",
        "hr_email",
    )

    list_filter = (
        "industry",
    )


# =========================================================
# PLACEMENT DRIVE
# =========================================================

@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "company",
        "job_title",
        "package",
        "location",
        "minimum_cgpa",
        "application_deadline",
        "status",
        "created_by",
    )

    list_filter = (
        "status",
        "location",
        "application_deadline",
    )

    search_fields = (
        "company__company_name",
        "job_title",
        "location",
        "allowed_departments",
    )

    autocomplete_fields = (
        "company",
        "created_by",
    )


# =========================================================
# JOB APPLICATION
# =========================================================

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "student",
        "placement_drive",
        "status",
        "application_date",
        "updated_at",
    )

    list_filter = (
        "status",
        "application_date",
        "placement_drive__company",
    )

    search_fields = (
        "student__student_id",
        "student__user__first_name",
        "student__user__last_name",
        "student__user__email",
        "placement_drive__job_title",
        "placement_drive__company__company_name",
    )

    autocomplete_fields = (
        "placement_drive",
    )