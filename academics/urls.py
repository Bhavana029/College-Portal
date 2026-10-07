from django.urls import path

from .views import (
    DepartmentListCreateView,
    DepartmentDetailView,

    StudentListCreateView,
    StudentDetailView,

    FacultyListCreateView,
    FacultyDetailView,

    SubjectListCreateView,
    SubjectDetailView,

    AttendanceListCreateView,
    AttendanceDetailView,

    MarksListCreateView,
    MarksDetailView,
)


urlpatterns = [

    # =====================================================
    # DEPARTMENTS
    # =====================================================

    path(
        "departments/",
        DepartmentListCreateView.as_view(),
        name="department-list-create",
    ),

    path(
        "departments/<int:pk>/",
        DepartmentDetailView.as_view(),
        name="department-detail",
    ),


    # =====================================================
    # STUDENTS
    # =====================================================

    path(
        "students/",
        StudentListCreateView.as_view(),
        name="student-list-create",
    ),

    path(
        "students/<int:pk>/",
        StudentDetailView.as_view(),
        name="student-detail",
    ),


    # =====================================================
    # FACULTY
    # =====================================================

    path(
        "faculty/",
        FacultyListCreateView.as_view(),
        name="faculty-list-create",
    ),

    path(
        "faculty/<int:pk>/",
        FacultyDetailView.as_view(),
        name="faculty-detail",
    ),


    # =====================================================
    # SUBJECTS
    # =====================================================

    path(
        "subjects/",
        SubjectListCreateView.as_view(),
        name="subject-list-create",
    ),

    path(
        "subjects/<int:pk>/",
        SubjectDetailView.as_view(),
        name="subject-detail",
    ),


    # =====================================================
    # ATTENDANCE
    # =====================================================

    path(
        "attendance/",
        AttendanceListCreateView.as_view(),
        name="attendance-list-create",
    ),

    path(
        "attendance/<int:pk>/",
        AttendanceDetailView.as_view(),
        name="attendance-detail",
    ),


    # =====================================================
    # MARKS
    # =====================================================

    path(
        "marks/",
        MarksListCreateView.as_view(),
        name="marks-list-create",
    ),

    path(
        "marks/<int:pk>/",
        MarksDetailView.as_view(),
        name="marks-detail",
    ),
]