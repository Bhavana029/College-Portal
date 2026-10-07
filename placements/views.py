from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import (
    Company,
    PlacementDrive,
    JobApplication,
)

from .serializers import (
    CompanySerializer,
    PlacementDriveSerializer,
    JobApplicationSerializer,
)

from accounts.permissions import (
    IsAdmin,
    IsAdminOrPlacementCell,
)

from academics.models import Student


# =========================================================
# COMPANY
# =========================================================

class CompanyListCreateView(generics.ListCreateAPIView):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.all().order_by("company_name")

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdminOrPlacementCell()]

    def perform_create(self, serializer):
        serializer.save()


# =========================================================
# COMPANY DETAIL
# =========================================================

class CompanyDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdminOrPlacementCell()]


# =========================================================
# PLACEMENT DRIVE
# =========================================================

class PlacementDriveListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = PlacementDriveSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = PlacementDrive.objects.select_related(
            "company",
            "created_by",
        ).all()

        # Student should see only open drives
        if user.role == "STUDENT":
            return queryset.filter(
                status="OPEN",
                application_deadline__gte=timezone.now().date(),
            )

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdminOrPlacementCell()]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


# =========================================================
# PLACEMENT DRIVE DETAIL
# =========================================================

class PlacementDriveDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = PlacementDriveSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = PlacementDrive.objects.select_related(
            "company",
            "created_by",
        ).all()

        if user.role == "STUDENT":
            return queryset.filter(
                status="OPEN",
                application_deadline__gte=timezone.now().date(),
            )

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]

        return [IsAdminOrPlacementCell()]


# =========================================================
# STUDENT APPLY FOR PLACEMENT
# =========================================================

class ApplyForPlacementView(
    generics.CreateAPIView
):
    serializer_class = JobApplicationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def create(self, request, *args, **kwargs):

        # Only Student can apply
        if request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can apply for placements."
            )

        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            raise PermissionDenied(
                "Student profile not found."
            )

        placement_id = self.kwargs.get("placement_id")

        placement = get_object_or_404(
            PlacementDrive,
            id=placement_id
        )

        # -------------------------------------------------
        # Check whether drive is open
        # -------------------------------------------------

        if placement.status != "OPEN":
            raise ValidationError(
                {
                    "message": (
                        "This placement drive is not currently open."
                    )
                }
            )

        # -------------------------------------------------
        # Check deadline
        # -------------------------------------------------

        if (
            placement.application_deadline
            < timezone.now().date()
        ):
            raise ValidationError(
                {
                    "message": (
                        "Application deadline has passed."
                    )
                }
            )

        # -------------------------------------------------
        # Check CGPA
        # -------------------------------------------------

        if student.cgpa < placement.minimum_cgpa:
            raise ValidationError(
                {
                    "message": (
                        "You are not eligible based on "
                        "the minimum CGPA requirement."
                    )
                }
            )

        # -------------------------------------------------
        # Check Department
        # -------------------------------------------------

        allowed_departments = [
            department.strip().upper()
            for department in (
                placement.allowed_departments.split(",")
            )
        ]

        student_department_code = (
            student.department.code.strip().upper()
        )

        student_department_name = (
            student.department.name.strip().upper()
        )

        department_allowed = (
            student_department_code in allowed_departments
            or student_department_name in allowed_departments
        )

        if not department_allowed:
            raise ValidationError(
                {
                    "message": (
                        "Your department is not eligible "
                        "for this placement."
                    )
                }
            )

        # -------------------------------------------------
        # Prevent duplicate application
        # -------------------------------------------------

        already_applied = JobApplication.objects.filter(
            student=student,
            placement_drive=placement,
        ).exists()

        if already_applied:
            raise ValidationError(
                {
                    "message": (
                        "You have already applied "
                        "for this placement."
                    )
                }
            )

        # -------------------------------------------------
        # Create application
        # -------------------------------------------------

        application = JobApplication.objects.create(
            student=student,
            placement_drive=placement,
            resume=request.FILES.get("resume"),
            status="APPLIED",
        )

        serializer = self.get_serializer(application)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# STUDENT'S OWN APPLICATIONS
# =========================================================

class MyApplicationsView(
    generics.ListAPIView
):
    serializer_class = JobApplicationSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can view their applications."
            )

        try:
            student = self.request.user.student_profile
        except Student.DoesNotExist:
            return JobApplication.objects.none()

        return JobApplication.objects.select_related(
            "student__user",
            "student__department",
            "placement_drive__company",
        ).filter(
            student=student
        )


# =========================================================
# ALL APPLICATIONS
# =========================================================

class AllApplicationsView(
    generics.ListAPIView
):
    serializer_class = JobApplicationSerializer

    def get_permissions(self):
        return [
            IsAdminOrPlacementCell()
        ]

    def get_queryset(self):
        queryset = JobApplication.objects.select_related(
            "student__user",
            "student__department",
            "placement_drive__company",
        ).all()

        # Optional filtering by placement drive
        placement_id = self.request.query_params.get(
            "placement_drive"
        )

        if placement_id:
            queryset = queryset.filter(
                placement_drive_id=placement_id
            )

        # Optional filtering by status
        application_status = (
            self.request.query_params.get("status")
        )

        if application_status:
            queryset = queryset.filter(
                status=application_status.upper()
            )

        # Optional filtering by department
        department = (
            self.request.query_params.get("department")
        )

        if department:
            queryset = queryset.filter(
                student__department__code__iexact=department
            )

        return queryset


# =========================================================
# APPLICATION DETAIL
# =========================================================

class ApplicationDetailView(
    generics.RetrieveAPIView
):
    serializer_class = JobApplicationSerializer

    def get_permissions(self):
        return [
            permissions.IsAuthenticated()
        ]

    def get_queryset(self):

        user = self.request.user

        queryset = JobApplication.objects.select_related(
            "student__user",
            "student__department",
            "placement_drive__company",
        )

        if user.role == "STUDENT":

            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return JobApplication.objects.none()

            return queryset.filter(
                student=student
            )

        if user.role in ["ADMIN", "PLACEMENT"]:
            return queryset

        return JobApplication.objects.none()


# =========================================================
# UPDATE APPLICATION STATUS
# =========================================================

class UpdateApplicationStatusView(
    generics.UpdateAPIView
):
    serializer_class = JobApplicationSerializer

    permission_classes = [
        IsAdminOrPlacementCell
    ]

    queryset = JobApplication.objects.select_related(
        "student__user",
        "student__department",
        "placement_drive__company",
    )

    http_method_names = [
        "patch",
        "put",
    ]

    def update(self, request, *args, **kwargs):

        application = self.get_object()

        new_status = request.data.get("status")

        allowed_statuses = [
            "APPLIED",
            "SHORTLISTED",
            "TEST",
            "INTERVIEW",
            "SELECTED",
            "REJECTED",
            "WITHDRAWN",
        ]

        if not new_status:
            return Response(
                {
                    "message": "Status is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = new_status.upper()

        if new_status not in allowed_statuses:
            return Response(
                {
                    "message": "Invalid application status.",
                    "allowed_statuses": allowed_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = new_status
        application.save()

        serializer = self.get_serializer(application)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )