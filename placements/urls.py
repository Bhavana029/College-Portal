from django.urls import path

from .views import (
    CompanyListCreateView,
    CompanyDetailView,
    PlacementDriveListCreateView,
    PlacementDriveDetailView,
    ApplyForPlacementView,
    MyApplicationsView,
    AllApplicationsView,
    ApplicationDetailView,
    UpdateApplicationStatusView,
)


urlpatterns = [

    # =====================================================
    # COMPANIES
    # =====================================================

    path(
        "companies/",
        CompanyListCreateView.as_view(),
        name="company-list-create",
    ),

    path(
        "companies/<int:pk>/",
        CompanyDetailView.as_view(),
        name="company-detail",
    ),


    # =====================================================
    # PLACEMENT DRIVES
    # =====================================================

    path(
        "drives/",
        PlacementDriveListCreateView.as_view(),
        name="placement-drive-list-create",
    ),

    path(
        "drives/<int:pk>/",
        PlacementDriveDetailView.as_view(),
        name="placement-drive-detail",
    ),


    # =====================================================
    # STUDENT APPLY
    # =====================================================

    path(
        "drives/<int:placement_id>/apply/",
        ApplyForPlacementView.as_view(),
        name="apply-for-placement",
    ),


    # =====================================================
    # STUDENT'S APPLICATIONS
    # =====================================================

    path(
        "my-applications/",
        MyApplicationsView.as_view(),
        name="my-applications",
    ),


    # =====================================================
    # ALL APPLICATIONS
    # ADMIN / PLACEMENT CELL
    # =====================================================

    path(
        "applications/",
        AllApplicationsView.as_view(),
        name="all-applications",
    ),

    path(
        "applications/<int:pk>/",
        ApplicationDetailView.as_view(),
        name="application-detail",
    ),


    # =====================================================
    # UPDATE APPLICATION STATUS
    # ADMIN / PLACEMENT CELL
    # =====================================================

    path(
        "applications/<int:pk>/status/",
        UpdateApplicationStatusView.as_view(),
        name="update-application-status",
    ),
]