from rest_framework import serializers

from .models import (
    Department,
    Student,
    Faculty,
    Subject,
    Attendance,
    Marks,
)


# =========================================================
# DEPARTMENT SERIALIZER
# =========================================================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
        ]
        read_only_fields = ["id"]


# =========================================================
# STUDENT SERIALIZER
# =========================================================

class StudentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "student_id",
            "user",
            "name",
            "email",
            "department",
            "year",
            "section",
            "batch",
            "cgpa",
        ]
        read_only_fields = [
            "id",
            "name",
            "email",
        ]

    def get_name(self, obj):
        return obj.user.get_full_name()


# =========================================================
# FACULTY SERIALIZER
# =========================================================

class FacultySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Faculty
        fields = [
            "id",
            "faculty_id",
            "user",
            "name",
            "email",
            "department",
            "designation",
        ]
        read_only_fields = [
            "id",
            "name",
            "email",
        ]

    def get_name(self, obj):
        return obj.user.get_full_name()


# =========================================================
# SUBJECT SERIALIZER
# =========================================================

class SubjectSerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "department",
            "department_name",
            "year",
            "semester",
            "faculty",
            "faculty_name",
        ]
        read_only_fields = [
            "id",
            "department_name",
            "faculty_name",
        ]

    def get_faculty_name(self, obj):
        return obj.faculty.user.get_full_name()


# =========================================================
# ATTENDANCE SERIALIZER
# =========================================================

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True,
    )
    subject_code = serializers.CharField(
        source="subject.code",
        read_only=True,
    )
    faculty_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "student",
            "student_name",
            "subject",
            "subject_name",
            "subject_code",
            "date",
            "status",
            "marked_by",
            "faculty_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "student_name",
            "subject_name",
            "subject_code",
            "faculty_name",
            "created_at",
        ]

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_faculty_name(self, obj):
        return obj.marked_by.user.get_full_name()


# =========================================================
# MARKS SERIALIZER
# =========================================================

class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True,
    )
    subject_code = serializers.CharField(
        source="subject.code",
        read_only=True,
    )
    faculty_name = serializers.SerializerMethodField()

    class Meta:
        model = Marks
        fields = [
            "id",
            "student",
            "student_name",
            "subject",
            "subject_name",
            "subject_code",
            "exam_name",
            "marks",
            "max_marks",
            "entered_by",
            "faculty_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "student_name",
            "subject_name",
            "subject_code",
            "faculty_name",
            "created_at",
        ]

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_faculty_name(self, obj):
        return obj.entered_by.user.get_full_name()

    def validate(self, data):
        marks = data.get("marks")
        max_marks = data.get(
            "max_marks",
            getattr(self.instance, "max_marks", 100),
        )

        if marks is not None and marks > max_marks:
            raise serializers.ValidationError(
                {
                    "marks": (
                        "Marks cannot be greater than "
                        "maximum marks."
                    )
                }
            )

        return data