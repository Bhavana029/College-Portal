from django.contrib import admin

from .models import (
    Department,
    Student,
    Faculty,
    Subject,
    Attendance,
    Marks,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "get_name",
        "department",
        "year",
        "section",
        "batch",
        "cgpa",
    )

    list_filter = (
        "department",
        "year",
        "section",
    )

    search_fields = (
        "student_id",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    def get_name(self, obj):
        return obj.user.get_full_name()

    get_name.short_description = "Student Name"


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = (
        "faculty_id",
        "get_name",
        "department",
        "designation",
    )

    list_filter = ("department",)

    search_fields = (
        "faculty_id",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    def get_name(self, obj):
        return obj.user.get_full_name()

    get_name.short_description = "Faculty Name"


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department",
        "year",
        "semester",
        "faculty",
    )

    list_filter = (
        "department",
        "year",
        "semester",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "date",
        "status",
        "marked_by",
    )

    list_filter = (
        "status",
        "date",
        "subject",
    )


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "exam_name",
        "marks",
        "max_marks",
        "entered_by",
    )

    list_filter = (
        "exam_name",
        "subject",
    )