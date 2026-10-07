from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import (
    html_login_view,
    html_logout_view,
)

from config.views import (
    # =====================================================
    # COMMON
    # =====================================================
    dashboard_redirect,

    # =====================================================
    # ADMIN
    # =====================================================
    admin_dashboard,
    admin_students,
    admin_student_add,
    admin_faculty,
    admin_faculty_add,
    admin_placement,
    admin_placement_add,

    # Announcements
    admin_announcement_add,
    admin_announcement_edit,
    admin_announcement_delete,

    # Holidays
    admin_holiday_add,
    admin_holiday_manage,
    admin_holiday_edit,
    admin_holiday_delete,

    # Password setup
    set_initial_password,

    # =====================================================
    # FACULTY
    # =====================================================
    faculty_dashboard,
    faculty_subjects,
    faculty_subject_add,
    faculty_subject_edit,
    faculty_subject_delete,
    faculty_attendance,
    faculty_marks,
    faculty_mark_add,
    faculty_mark_edit,
    faculty_mark_delete,

    # =====================================================
    # PLACEMENT CELL
    # =====================================================
    placement_dashboard,
    placement_companies,
    placement_company_add,
    placement_company_edit,
    placement_company_delete,
    placement_drives,
    placement_drive_add,
    placement_drive_edit,
    placement_drive_delete,
    user_announcements,
    # =====================================================
    # STUDENT
    # =====================================================
    student_dashboard,
    student_attendance,
    student_marks,
    student_apply_placement,
    student_applications,

    placement_applications,
    placement_application_status_update, student_placements,
)


urlpatterns = [

    # =====================================================
    # LOGIN / LOGOUT
    # =====================================================

    path(
        "",
        html_login_view,
        name="home",
    ),

    path(
        "login/",
        html_login_view,
        name="login",
    ),

    path(
        "logout/",
        html_logout_view,
        name="logout",
    ),


    # =====================================================
    # DJANGO ADMIN
    # =====================================================

    path(
        "admin/",
        admin.site.urls,
    ),


    # =====================================================
    # COMMON DASHBOARD
    # =====================================================

    path(
        "dashboard/",
        dashboard_redirect,
        name="dashboard",
    ),


    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    path(
        "admin-dashboard/",
        admin_dashboard,
        name="admin-dashboard",
    ),

    # -----------------------------------------------------
    # Students
    # -----------------------------------------------------

    path(
        "admin-dashboard/students/",
        admin_students,
        name="admin-students",
    ),

    path(
        "admin-dashboard/students/add/",
        admin_student_add,
        name="admin-student-add",
    ),
# =====================================================
# STUDENT PLACEMENTS
# =====================================================

path(
    "student/placements/",
    student_placements,
    name="student-placements",
),

path(
    "student/placements/<int:drive_id>/apply/",
    student_apply_placement,
    name="student-apply-placement",
),

path(
    "student/applications/",
    student_applications,
    name="student-applications",
),

    # -----------------------------------------------------
    # Faculty
    # -----------------------------------------------------

    path(
        "admin-dashboard/faculty/",
        admin_faculty,
        name="admin-faculty",
    ),

    path(
        "admin-dashboard/faculty/add/",
        admin_faculty_add,
        name="admin-faculty-add",
    ),


    # -----------------------------------------------------
    # Placement Officer
    # -----------------------------------------------------

    path(
        "admin-dashboard/placement/",
        admin_placement,
        name="admin-placement",
    ),

    path(
        "admin-dashboard/placement/add/",
        admin_placement_add,
        name="admin-placement-add",
    ),


    # =====================================================
    # ADMIN - ANNOUNCEMENTS
    # =====================================================

    # Add + View List
    path(
        "admin-dashboard/announcement/add/",
        admin_announcement_add,
        name="admin-announcement-add",
    ),

    # Edit
    path(
        "admin-dashboard/announcement/<int:announcement_id>/edit/",
        admin_announcement_edit,
        name="admin-announcement-edit",
    ),

    # Delete
    path(
        "admin-dashboard/announcement/<int:announcement_id>/delete/",
        admin_announcement_delete,
        name="admin-announcement-delete",
    ),


    # =====================================================
    # ADMIN - HOLIDAYS
    # =====================================================

    # Main Holiday page - Add + List
    path(
        "admin-dashboard/holiday/add/",
        admin_holiday_manage,
        name="admin-holiday-manage",
    ),

    # Old/simple Add Holiday route
    path(
        "admin-dashboard/holiday/create/",
        admin_holiday_add,
        name="admin-holiday-add",
    ),

    # Edit
    path(
        "admin-dashboard/holiday/<int:holiday_id>/edit/",
        admin_holiday_edit,
        name="admin-holiday-edit",
    ),

    # Delete
    path(
        "admin-dashboard/holiday/<int:holiday_id>/delete/",
        admin_holiday_delete,
        name="admin-holiday-delete",
    ),


    # =====================================================
    # PASSWORD SETUP
    # =====================================================

    path(
        "set-password/<uidb64>/<token>/",
        set_initial_password,
        name="set-initial-password",
    ),


    # =====================================================
    # FACULTY
    # =====================================================

    path(
        "faculty-dashboard/",
        faculty_dashboard,
        name="faculty-dashboard",
    ),


    # -----------------------------------------------------
    # Subjects
    # -----------------------------------------------------

    path(
        "faculty/subjects/",
        faculty_subjects,
        name="faculty-subjects",
    ),

    path(
        "faculty/subjects/add/",
        faculty_subject_add,
        name="faculty-subject-add",
    ),

    path(
        "faculty/subjects/<int:subject_id>/edit/",
        faculty_subject_edit,
        name="faculty-subject-edit",
    ),

    path(
        "faculty/subjects/<int:subject_id>/delete/",
        faculty_subject_delete,
        name="faculty-subject-delete",
    ),


    # -----------------------------------------------------
    # Attendance
    # -----------------------------------------------------

    path(
        "faculty/attendance/",
        faculty_attendance,
        name="faculty-attendance",
    ),


    # -----------------------------------------------------
    # Marks
    # -----------------------------------------------------

    path(
        "faculty/marks/",
        faculty_marks,
        name="faculty-marks",
    ),

    path(
        "faculty/marks/<int:student_id>/add/",
        faculty_mark_add,
        name="faculty-mark-add",
    ),

    path(
        "faculty/marks/<int:mark_id>/edit/",
        faculty_mark_edit,
        name="faculty-mark-edit",
    ),

    path(
        "faculty/marks/<int:mark_id>/delete/",
        faculty_mark_delete,
        name="faculty-mark-delete",
    ),


    # =====================================================
    # PLACEMENT CELL
    # =====================================================

    path(
        "placement-dashboard/",
        placement_dashboard,
        name="placement-dashboard",
    ),


    # -----------------------------------------------------
    # Companies
    # -----------------------------------------------------

    path(
        "placement/companies/",
        placement_companies,
        name="placement-companies",
    ),

    path(
        "placement/companies/add/",
        placement_company_add,
        name="placement-company-add",
    ),

    path(
        "placement/companies/<int:company_id>/edit/",
        placement_company_edit,
        name="placement-company-edit",
    ),

    path(
        "placement/companies/<int:company_id>/delete/",
        placement_company_delete,
        name="placement-company-delete",
    ),


    # -----------------------------------------------------
    # Placement Drives
    # -----------------------------------------------------

    path(
        "placement/drives/",
        placement_drives,
        name="placement-drives",
    ),

    path(
        "placement/drives/add/",
        placement_drive_add,
        name="placement-drive-add",
    ),

    path(
        "placement/drives/<int:drive_id>/edit/",
        placement_drive_edit,
        name="placement-drive-edit",
    ),

    path(
        "placement/drives/<int:drive_id>/delete/",
        placement_drive_delete,
        name="placement-drive-delete",
    ),

# =====================================================
# PLACEMENT APPLICATIONS
# =====================================================

path(
    "placement/applications/",
    placement_applications,
    name="placement-applications",
),

path(
    "placement/applications/<int:application_id>/status/",
    placement_application_status_update,
    name="placement-application-status-update",
),
    # =====================================================
    # STUDENT
    # =====================================================

    path(
        "student-dashboard/",
        student_dashboard,
        name="student-dashboard",
    ),


    # =====================================================
    # APIs
    # =====================================================

    path(
        "api/auth/",
        include("accounts.urls"),
    ),

    path(
        "api/academics/",
        include("academics.urls"),
    ),

    path(
        "api/placements/",
        include("placements.urls"),
    ),

    path(
        "api/notifications/",
        include("notifications.urls"),
    ),
# =====================================================
# USER ANNOUNCEMENTS + HOLIDAYS
# =====================================================

path(
    "announcements/",
    user_announcements,
    name="user-announcements",
),
path(
    "student/attendance/",
    student_attendance,
    name="student-attendance",
),
path(
    "student/marks/",
    student_marks,
    name="student-marks",
),
]


# =========================================================
# MEDIA FILES
# =========================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )