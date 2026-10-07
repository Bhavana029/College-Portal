from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import (
    Department,
    Student,
    Faculty,
    Subject,
    Attendance,
    Marks,
)

from .serializers import (
    DepartmentSerializer,
    StudentSerializer,
    FacultySerializer,
    SubjectSerializer,
    AttendanceSerializer,
    MarksSerializer,
)


# =========================================================
# HELPER
# =========================================================

def get_user_role(request):
    return request.user.role


# =========================================================
# DEPARTMENT
# =========================================================

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdmin()]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if get_user_role(self.request) != "ADMIN":
            raise PermissionDenied(
                "Only Admin can update departments."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if get_user_role(self.request) != "ADMIN":
            raise PermissionDenied(
                "Only Admin can delete departments."
            )

        instance.delete()


# =========================================================
# STUDENTS
# =========================================================

class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        return Student.objects.select_related(
            "user",
            "department",
        ).all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdmin()]

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only Admin can create students."
            )

        serializer.save()


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related(
        "user",
        "department",
    )
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)

        if request.user.role == "ADMIN":
            return

        if (
            request.user.role == "STUDENT"
            and obj.user == request.user
        ):
            return

        raise PermissionDenied(
            "You do not have permission to access this student."
        )


# =========================================================
# FACULTY
# =========================================================

class FacultyListCreateView(generics.ListCreateAPIView):
    serializer_class = FacultySerializer

    def get_queryset(self):
        return Faculty.objects.select_related(
            "user",
            "department",
        ).all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdmin()]

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only Admin can create faculty."
            )

        serializer.save()


class FacultyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Faculty.objects.select_related(
        "user",
        "department",
    )
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only Admin can update faculty."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only Admin can delete faculty."
            )

        instance.delete()


# =========================================================
# SUBJECTS
# =========================================================

class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        queryset = Subject.objects.select_related(
            "department",
            "faculty__user",
        ).all()

        user = self.request.user

        if user.role == "FACULTY":
            try:
                faculty = user.faculty_profile
                queryset = queryset.filter(
                    faculty=faculty
                )
            except Faculty.DoesNotExist:
                return Subject.objects.none()

        elif user.role == "STUDENT":
            try:
                student = user.student_profile
                queryset = queryset.filter(
                    department=student.department
                )
            except Student.DoesNotExist:
                return Subject.objects.none()

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdmin()]

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only Admin can create subjects."
            )

        serializer.save()


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.select_related(
        "department",
        "faculty__user",
    )
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only Admin can update subjects."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only Admin can delete subjects."
            )

        instance.delete()


# =========================================================
# ATTENDANCE
# =========================================================

class AttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Attendance.objects.select_related(
            "student__user",
            "subject",
            "marked_by__user",
        ).all()

        if user.role == "STUDENT":
            try:
                student = user.student_profile
                return queryset.filter(student=student)
            except Student.DoesNotExist:
                return Attendance.objects.none()

        if user.role == "FACULTY":
            try:
                faculty = user.faculty_profile
                return queryset.filter(
                    marked_by=faculty
                )
            except Faculty.DoesNotExist:
                return Attendance.objects.none()

        if user.role == "ADMIN":
            return queryset

        return Attendance.objects.none()

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.role != "FACULTY":
            raise PermissionDenied(
                "Only Faculty can mark attendance."
            )

        try:
            faculty = self.request.user.faculty_profile
        except Faculty.DoesNotExist:
            raise PermissionDenied(
                "Faculty profile not found."
            )

        student = get_object_or_404(
            Student,
            id=self.request.data.get("student"),
        )

        subject = get_object_or_404(
            Subject,
            id=self.request.data.get("subject"),
        )

        # Faculty can mark attendance only for their subject
        if subject.faculty != faculty:
            raise PermissionDenied(
                "You can mark attendance only for your subjects."
            )

        # Student must belong to the same department
        if student.department != subject.department:
            raise PermissionDenied(
                "Student does not belong to this department."
            )

        serializer.save(
            marked_by=faculty
        )


# =========================================================
# ATTENDANCE DETAIL
# =========================================================

class AttendanceDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Attendance.objects.select_related(
            "student__user",
            "subject",
            "marked_by__user",
        )

    def perform_update(self, serializer):
        if self.request.user.role != "FACULTY":
            raise PermissionDenied(
                "Only Faculty can update attendance."
            )

        try:
            faculty = self.request.user.faculty_profile
        except Faculty.DoesNotExist:
            raise PermissionDenied(
                "Faculty profile not found."
            )

        attendance = self.get_object()

        if attendance.marked_by != faculty:
            raise PermissionDenied(
                "You can update only your attendance records."
            )

        serializer.save(
            marked_by=faculty
        )

    def perform_destroy(self, instance):
        if self.request.user.role != "FACULTY":
            raise PermissionDenied(
                "Only Faculty can delete attendance."
            )

        if instance.marked_by != self.request.user.faculty_profile:
            raise PermissionDenied(
                "You can delete only your attendance records."
            )

        instance.delete()


# =========================================================
# MARKS
# =========================================================

class MarksListCreateView(generics.ListCreateAPIView):
    serializer_class = MarksSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Marks.objects.select_related(
            "student__user",
            "subject",
            "entered_by__user",
        ).all()

        if user.role == "STUDENT":
            try:
                student = user.student_profile
                return queryset.filter(student=student)
            except Student.DoesNotExist:
                return Marks.objects.none()

        if user.role == "FACULTY":
            try:
                faculty = user.faculty_profile
                return queryset.filter(
                    entered_by=faculty
                )
            except Faculty.DoesNotExist:
                return Marks.objects.none()

        if user.role == "ADMIN":
            return queryset

        return Marks.objects.none()

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.role != "FACULTY":
            raise PermissionDenied(
                "Only Faculty can enter marks."
            )

        try:
            faculty = self.request.user.faculty_profile
        except Faculty.DoesNotExist:
            raise PermissionDenied(
                "Faculty profile not found."
            )

        student = get_object_or_404(
            Student,
            id=self.request.data.get("student"),
        )

        subject = get_object_or_404(
            Subject,
            id=self.request.data.get("subject"),
        )

        # Faculty can enter marks only for their subjects
        if subject.faculty != faculty:
            raise PermissionDenied(
                "You can enter marks only for your subjects."
            )

        # Student must belong to the same department
        if student.department != subject.department:
            raise PermissionDenied(
                "Student does not belong to this department."
            )

        serializer.save(
            entered_by=faculty
        )


# =========================================================
# MARKS DETAIL
# =========================================================

class MarksDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = MarksSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Marks.objects.select_related(
            "student__user",
            "subject",
            "entered_by__user",
        )

    def perform_update(self, serializer):
        if self.request.user.role != "FACULTY":
            raise PermissionDenied(
                "Only Faculty can update marks."
            )

        try:
            faculty = self.request.user.faculty_profile
        except Faculty.DoesNotExist:
            raise PermissionDenied(
                "Faculty profile not found."
            )

        marks = self.get_object()

        if marks.entered_by != faculty:
            raise PermissionDenied(
                "You can update only your marks records."
            )

        serializer.save(
            entered_by=faculty
        )

    def perform_destroy(self, instance):
        if self.request.user.role != "FACULTY":
            raise PermissionDenied(
                "Only Faculty can delete marks."
            )

        if instance.entered_by != self.request.user.faculty_profile:
            raise PermissionDenied(
                "You can delete only your marks records."
            )

        instance.delete()


# =========================================================
# CUSTOM ADMIN PERMISSION
# =========================================================

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to Admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )