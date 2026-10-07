from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from decimal import Decimal, InvalidOperation
from django.conf import settings
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db import transaction
from django.core.mail import send_mail
from academics.models import (
    Department,
    Student,
    Faculty,
    Subject,
    Attendance,
    Marks,
)

from placements.models import (
    Company,
    PlacementDrive,
    JobApplication,
)

from notifications.models import (
    Announcement,
    Holiday,
)

User = get_user_model()
# =========================================================
# COMMON DASHBOARD REDIRECT
# =========================================================

@login_required
def dashboard_redirect(request):

    user = request.user

    if user.is_superuser or user.role == "ADMIN":
        return redirect("admin-dashboard")

    if user.role == "FACULTY":
        return redirect("faculty-dashboard")

    if user.role == "PLACEMENT":
        return redirect("placement-dashboard")

    if user.role == "STUDENT":
        return redirect("student-dashboard")

    return redirect("login")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@login_required
def admin_dashboard(request):

    # Only Admin / Superuser
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    context = {
        "total_students": Student.objects.count(),

        "total_faculty": Faculty.objects.count(),

        "total_placements": PlacementDrive.objects.count(),

        "total_applications": JobApplication.objects.count(),

        "total_announcements": Announcement.objects.count(),

        "total_holidays": Holiday.objects.count(),

        "recent_placements": PlacementDrive.objects.select_related(
            "company"
        ).order_by("-created_at")[:5],

        "recent_announcements": Announcement.objects.order_by(
            "-created_at"
        )[:5],
    }

    return render(
        request,
        "admin/dashboard.html",
        context,
    )

def create_password_setup_link(request, user):
    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = default_token_generator.make_token(user)

    return request.build_absolute_uri(
        reverse(
            "set-initial-password",
            kwargs={
                "uidb64": uid,
                "token": token,
            }
        )
    )

@login_required
def admin_students(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    students = Student.objects.select_related(
        "user",
        "department"
    ).order_by(
        "student_id"
    )

    return render(
        request,
        "admin/students.html",
        {
            "students": students
        }
    )
@login_required
def admin_student_add(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    departments = Department.objects.all().order_by("name")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        student_id = request.POST.get("student_id", "").strip()
        department_id = request.POST.get("department")
        year = request.POST.get("year")
        section = request.POST.get("section", "").strip()
        batch = request.POST.get("batch", "").strip()
        cgpa = request.POST.get("cgpa", "").strip()

        if not username or not first_name or not student_id:
            messages.error(
                request,
                "Username, first name and student ID are required."
            )
            return redirect("admin-student-add")

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return redirect("admin-student-add")

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(
                request,
                "Student ID already exists."
            )
            return redirect("admin-student-add")

        department = get_object_or_404(
            Department,
            id=department_id
        )

        try:
            year_value = int(year)
        except (TypeError, ValueError):
            messages.error(
                request,
                "Invalid year."
            )
            return redirect("admin-student-add")

        if cgpa:
            try:
                cgpa_value = float(cgpa)
            except ValueError:
                messages.error(
                    request,
                    "Invalid CGPA."
                )
                return redirect("admin-student-add")
        else:
            cgpa_value = 0

        if year_value not in [1, 2, 3, 4]:
            messages.error(
                request,
                "Year must be between 1 and 4."
            )
            return redirect("admin-student-add")

        if cgpa_value < 0 or cgpa_value > 10:
            messages.error(
                request,
                "CGPA must be between 0 and 10."
            )
            return redirect("admin-student-add")

        with transaction.atomic():

            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                role="STUDENT",
            )

            user.set_unusable_password()
            user.save()

            Student.objects.create(
                user=user,
                student_id=student_id,
                department=department,
                year=year_value,
                section=section,
                batch=batch,
                cgpa=cgpa_value,
            )

        if not user.email:
            messages.error(
                request,
                "Student created, but no email address was provided. Password setup link could not be sent."
            )

            return redirect(
                "admin-students"
            )

        try:
            setup_link = send_password_setup_email(
                request,
                user,
                "Student"
            )

        except Exception:
            messages.error(
                request,
                "Student was created, but the password setup email could not be sent."
            )

            return redirect(
                "admin-students"
            )

        messages.success(
            request,
            f"Student created successfully. Password setup link sent to {user.email}."
        )

        return redirect(
            "admin-students"
        )

    return render(
        request,
        "admin/student_form.html",
        {
            "departments": departments,
        }
    )
@login_required
def admin_faculty(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    faculty_members = Faculty.objects.select_related(
        "user",
        "department"
    ).order_by(
        "faculty_id"
    )

    return render(
        request,
        "admin/faculty.html",
        {
            "faculty_members": faculty_members
        }
    )
@login_required
def admin_faculty_add(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    departments = Department.objects.all().order_by("name")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        faculty_id = request.POST.get("faculty_id", "").strip()
        department_id = request.POST.get("department")
        designation = request.POST.get(
            "designation",
            ""
        ).strip()

        if not username or not first_name or not faculty_id:
            messages.error(
                request,
                "Username, first name and faculty ID are required."
            )
            return redirect("admin-faculty-add")

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return redirect("admin-faculty-add")

        if Faculty.objects.filter(
            faculty_id=faculty_id
        ).exists():

            messages.error(
                request,
                "Faculty ID already exists."
            )
            return redirect("admin-faculty-add")

        department = get_object_or_404(
            Department,
            id=department_id
        )

        with transaction.atomic():

            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                role="FACULTY",
            )

            user.set_unusable_password()
            user.save()

            Faculty.objects.create(
                user=user,
                faculty_id=faculty_id,
                department=department,
                designation=designation,
            )

        if not user.email:
            messages.error(
                request,
                "Faculty created, but no email address was provided."
            )
            return redirect("admin-faculty")

        try:
            send_password_setup_email(
                request,
                user,
                "Faculty"
            )
        except Exception:
            messages.error(
                request,
                "Faculty created, but the password setup email could not be sent."
            )
            return redirect("admin-faculty")

        messages.success(
            request,
            f"Faculty created successfully. Password setup link sent to {user.email}."
        )

        return redirect("admin-faculty")

    return render(
        request,
        "admin/faculty_form.html",
        {
            "departments": departments,
        }
    )

@login_required
def admin_placement(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    placement_users = User.objects.filter(
        role="PLACEMENT"
    ).order_by(
        "username"
    )

    companies = Company.objects.all().order_by(
        "company_name"
    )

    drives = PlacementDrive.objects.select_related(
        "company"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "admin/placement.html",
        {
            "placement_users": placement_users,
            "companies": companies,
            "drives": drives,
        }
    )
@login_required
def admin_placement_add(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        if not username or not first_name:
            messages.error(
                request,
                "Username and first name are required."
            )
            return redirect(
                "admin-placement-add"
            )

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect(
                "admin-placement-add"
            )

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role="PLACEMENT",
        )

        user.set_unusable_password()
        user.save()

        if not user.email:
            messages.error(
                request,
                "Placement Officer created, but no email address was provided."
            )
            return redirect("admin-placement")

        try:
            send_password_setup_email(
                request,
                user,
                "Placement Officer"
            )
        except Exception:
            messages.error(
                request,
                "Placement Officer created, but the password setup email could not be sent."
            )
            return redirect("admin-placement")

        messages.success(
            request,
            f"Placement Officer created successfully. Password setup link sent to {user.email}."
        )

        return redirect("admin-placement")

    return render(
        request,
        "admin/placement_form.html"
    )

def set_initial_password(
    request,
    uidb64,
    token
):

    try:

        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        user = User.objects.get(
            pk=uid
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):

        return render(
            request,
            "registration/invalid_setup_link.html"
        )

    if not default_token_generator.check_token(
        user,
        token
    ):

        return render(
            request,
            "registration/invalid_setup_link.html"
        )

    if request.method == "POST":

        password1 = request.POST.get(
            "password1"
        )

        password2 = request.POST.get(
            "password2"
        )

        if not password1 or not password2:

            messages.error(
                request,
                "Please enter both passwords."
            )

        elif password1 != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

        elif len(password1) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

        else:

            user.set_password(
                password1
            )

            user.save()

            messages.success(
                request,
                "Password created successfully. You can now login."
            )

            return redirect(
                "login"
            )

    return render(
        request,
        "registration/set_initial_password.html",
        {
            "user": user
        }
    )
@login_required
def admin_announcement_add(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        audience = request.POST.get(
            "audience",
            "ALL"
        )

        if not title or not description:
            messages.error(
                request,
                "Title and description are required."
            )

            return redirect(
                "admin-announcement-add"
            )

        Announcement.objects.create(
            title=title,
            description=description,
            audience=audience,
            created_by=request.user,
        )

        messages.success(
            request,
            "Announcement published successfully."
        )

        return redirect(
            "admin-dashboard"
        )

    return render(
        request,
        "admin/announcement_form.html"
    )
@login_required
def admin_holiday_add(request):
    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        date = request.POST.get(
            "date"
        )

        description = request.POST.get(
            "description",
            ""
        ).strip()

        if not title or not date:

            messages.error(
                request,
                "Holiday title and date are required."
            )

            return redirect(
                "admin-holiday-add"
            )

        Holiday.objects.create(
            title=title,
            date=date,
            description=description,
            created_by=request.user,
        )

        messages.success(
            request,
            "Holiday added successfully."
        )

        return redirect(
            "admin-dashboard"
        )

    return render(
        request,
        "admin/holiday_form.html"
    )
# =========================================================
# FACULTY DASHBOARD
# =========================================================

@login_required
def faculty_dashboard(request):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        return redirect("login")

    subjects = Subject.objects.filter(
        faculty=faculty
    ).select_related("department").order_by("year", "semester", "name")

    total_subjects = subjects.count()

    total_students = Student.objects.filter(
        department=faculty.department
    ).count()

    total_attendance = Attendance.objects.filter(
        marked_by=faculty
    ).count()

    today_attendance = Attendance.objects.filter(
        marked_by=faculty,
        date=timezone.localdate()
    ).count()

    total_marks = Marks.objects.filter(
        entered_by=faculty
    ).count()

    recent_attendance = Attendance.objects.filter(
        marked_by=faculty
    ).select_related(
        "student__user",
        "subject"
    ).order_by(
        "-date",
        "-created_at"
    )[:5]

    recent_marks = Marks.objects.filter(
        entered_by=faculty
    ).select_related(
        "student__user",
        "subject"
    ).order_by(
        "-created_at"
    )[:5]

    context = {
        "faculty": faculty,
        "subjects": subjects,
        "total_subjects": total_subjects,
        "total_students": total_students,
        "total_attendance": total_attendance,
        "today_attendance": today_attendance,
        "total_marks": total_marks,
        "recent_attendance": recent_attendance,
        "recent_marks": recent_marks,
    }

    return render(request, "faculty/dashboard.html", context)

@login_required
def faculty_attendance(request):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    # -----------------------------
    # Selected filters
    # -----------------------------

    selected_year = (
        request.GET.get("year")
        or request.POST.get("year")
        or ""
    )

    selected_semester = (
        request.GET.get("semester")
        or request.POST.get("semester")
        or ""
    )

    selected_subject_id = (
        request.GET.get("subject")
        or request.POST.get("subject")
        or ""
    )

    selected_date = (
        request.GET.get("date")
        or request.POST.get("date")
        or timezone.localdate().isoformat()
    )

    # Edit mode
    edit_mode = request.GET.get("edit") == "1"

    # -----------------------------
    # Year choices
    # -----------------------------

    years = [1, 2, 3, 4]

    # -----------------------------
    # Semester choices
    # -----------------------------

    semesters = list(range(1, 9))

    # -----------------------------
    # Faculty subjects
    # -----------------------------

    subjects = Subject.objects.filter(
        faculty=faculty
    ).select_related(
        "department"
    ).order_by(
        "year",
        "semester",
        "name"
    )

    # Filter subjects by year
    if selected_year:
        try:
            selected_year_int = int(selected_year)

            subjects = subjects.filter(
                year=selected_year_int
            )

        except ValueError:
            selected_year_int = None
    else:
        selected_year_int = None

    # Filter subjects by semester
    if selected_semester:
        try:
            selected_semester_int = int(selected_semester)

            subjects = subjects.filter(
                semester=selected_semester_int
            )

        except ValueError:
            selected_semester_int = None
    else:
        selected_semester_int = None

    # -----------------------------
    # Selected subject
    # -----------------------------

    selected_subject = None

    if selected_subject_id:

        try:

            selected_subject = subjects.get(
                id=selected_subject_id
            )

        except Subject.DoesNotExist:

            selected_subject = None

            messages.error(
                request,
                "Invalid subject selection."
            )

    # -----------------------------
    # Students
    # -----------------------------

    students = Student.objects.none()

    student_rows = []

    attendance_saved = False
    all_students_marked = False

    if selected_subject:

        students = Student.objects.filter(
            department=faculty.department,
            year=selected_subject.year
        ).select_related(
            "user",
            "department"
        ).order_by(
            "student_id"
        )

        # Existing attendance
        existing_records = Attendance.objects.filter(
            subject=selected_subject,
            date=selected_date
        )

        attendance_map = {
            record.student_id: record.status
            for record in existing_records
        }

        # Check whether attendance already exists
        if students.exists():

            all_students_marked = (
                existing_records.filter(
                    student__in=students
                ).count()
                == students.count()
            )

        # -----------------------------
        # Save Attendance
        # -----------------------------

        if request.method == "POST" and (
                not all_students_marked or edit_mode
        ):

            try:

                attendance_date = datetime.strptime(
                    selected_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                messages.error(
                    request,
                    "Invalid date."
                )

                return redirect(
                    "faculty-attendance"
                )

            for student in students:

                status = request.POST.get(
                    f"status_{student.id}"
                )

                if status not in [
                    "PRESENT",
                    "ABSENT"
                ]:
                    continue

                Attendance.objects.update_or_create(
                    student=student,
                    subject=selected_subject,
                    date=attendance_date,
                    defaults={
                        "status": status,
                        "marked_by": faculty,
                    }
                )

            messages.success(
                request,
                "Attendance saved successfully."
            )

            return redirect(
                f"/faculty/attendance/"
                f"?year={selected_subject.year}"
                f"&semester={selected_subject.semester}"
                f"&subject={selected_subject.id}"
                f"&date={selected_date}"
            )

        # -----------------------------
        # Prepare student rows
        # -----------------------------

        for student in students:

            student_rows.append({
                "student": student,
                "status": attendance_map.get(
                    student.id,
                    ""
                )
            })

        attendance_saved = all_students_marked

    # -----------------------------
    # Context
    # -----------------------------

    context = {

        "faculty": faculty,

        "years": years,

        "semesters": semesters,

        "subjects": subjects,

        "students": students,

        "student_rows": student_rows,

        "selected_year": selected_year,

        "selected_semester": selected_semester,

        "selected_subject": selected_subject,

        "selected_subject_id": selected_subject_id,

        "selected_date": selected_date,

        "attendance_saved": attendance_saved,

        "all_students_marked": all_students_marked,

        "edit_mode": edit_mode,
    }

    return render(
        request,
        "faculty/attendance.html",
        context
    )



@login_required
@login_required
def faculty_subjects(request):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    # Get filter values
    selected_year = request.GET.get("year", "")
    selected_semester = request.GET.get("semester", "")

    # Only subjects belonging to logged-in faculty
    subjects = Subject.objects.filter(
        faculty=faculty
    ).select_related(
        "department"
    ).order_by(
        "year",
        "semester",
        "name"
    )

    # Filter by year
    if selected_year:
        try:
            subjects = subjects.filter(
                year=int(selected_year)
            )
        except ValueError:
            selected_year = ""

    # Filter by semester
    if selected_semester:
        try:
            subjects = subjects.filter(
                semester=int(selected_semester)
            )
        except ValueError:
            selected_semester = ""

    # Group filtered subjects
    grouped_subjects = {}

    for subject in subjects:

        if subject.year not in grouped_subjects:
            grouped_subjects[subject.year] = {}

        if subject.semester not in grouped_subjects[subject.year]:
            grouped_subjects[subject.year][subject.semester] = []

        grouped_subjects[subject.year][subject.semester].append(subject)

    context = {
        "faculty": faculty,
        "subjects": subjects,
        "grouped_subjects": grouped_subjects,

        "selected_year": selected_year,
        "selected_semester": selected_semester,

        "years": [1, 2, 3, 4],
        "semesters": list(range(1, 9)),
    }

    return render(
        request,
        "faculty/subjects.html",
        context
    )

@login_required
def faculty_subject_add(request):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip().upper()
        year = request.POST.get("year")
        semester = request.POST.get("semester")

        if not name or not code or not year or not semester:
            messages.error(
                request,
                "Please fill all required fields."
            )
            return redirect("faculty-subject-add")

        try:
            year = int(year)
            semester = int(semester)
        except ValueError:
            messages.error(
                request,
                "Year and semester must be valid numbers."
            )
            return redirect("faculty-subject-add")

        if year not in [1, 2, 3, 4]:
            messages.error(
                request,
                "Year must be between 1 and 4."
            )
            return redirect("faculty-subject-add")

        if semester not in range(1, 9):
            messages.error(
                request,
                "Semester must be between 1 and 8."
            )
            return redirect("faculty-subject-add")

        if Subject.objects.filter(code=code).exists():
            messages.error(
                request,
                "Subject code already exists."
            )
            return redirect("faculty-subject-add")

        Subject.objects.create(
            name=name,
            code=code,
            department=faculty.department,
            year=year,
            semester=semester,
            faculty=faculty,
        )

        messages.success(
            request,
            "Subject added successfully."
        )

        return redirect("faculty-subjects")

    return render(
        request,
        "faculty/subject_form.html",
        {
            "faculty": faculty,
            "page_title": "Add Subject",
            "button_text": "Add Subject",
        }
    )


@login_required
def faculty_subject_edit(request, subject_id):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        faculty=faculty
    )

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip().upper()
        year = request.POST.get("year")
        semester = request.POST.get("semester")

        if not name or not code or not year or not semester:
            messages.error(
                request,
                "Please fill all required fields."
            )
            return redirect(
                "faculty-subject-edit",
                subject_id=subject.id
            )

        try:
            year = int(year)
            semester = int(semester)
        except ValueError:
            messages.error(
                request,
                "Year and semester must be valid numbers."
            )
            return redirect(
                "faculty-subject-edit",
                subject_id=subject.id
            )

        if year not in [1, 2, 3, 4]:
            messages.error(
                request,
                "Year must be between 1 and 4."
            )
            return redirect(
                "faculty-subject-edit",
                subject_id=subject.id
            )

        if semester not in range(1, 9):
            messages.error(
                request,
                "Semester must be between 1 and 8."
            )
            return redirect(
                "faculty-subject-edit",
                subject_id=subject.id
            )

        if Subject.objects.filter(
            code=code
        ).exclude(
            id=subject.id
        ).exists():

            messages.error(
                request,
                "Another subject already uses this code."
            )

            return redirect(
                "faculty-subject-edit",
                subject_id=subject.id
            )

        subject.name = name
        subject.code = code
        subject.year = year
        subject.semester = semester

        subject.save()

        messages.success(
            request,
            "Subject updated successfully."
        )

        return redirect("faculty-subjects")

    return render(
        request,
        "faculty/subject_form.html",
        {
            "faculty": faculty,
            "subject": subject,
            "page_title": "Edit Subject",
            "button_text": "Save Changes",
        }
    )


@login_required
def faculty_subject_delete(request, subject_id):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        faculty=faculty
    )

    if request.method == "POST":

        subject.delete()

        messages.success(
            request,
            "Subject deleted successfully."
        )

    return redirect("faculty-subjects")

@login_required
def faculty_marks(request):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    selected_year = request.GET.get("year", "")
    selected_semester = request.GET.get("semester", "")

    years = [1, 2, 3, 4]
    semesters = list(range(1, 9))

    students = Student.objects.none()

    subjects = Subject.objects.none()

    student_data = []

    # Only show data after both filters are selected
    if selected_year and selected_semester:

        try:
            year = int(selected_year)
            semester = int(selected_semester)
        except ValueError:
            year = None
            semester = None

        if year and semester:

            students = Student.objects.filter(
                department=faculty.department,
                year=year
            ).select_related(
                "user",
                "department"
            ).order_by(
                "student_id"
            )

            # Only subjects assigned to this faculty
            subjects = Subject.objects.filter(
                faculty=faculty,
                year=year,
                semester=semester
            ).select_related(
                "department"
            ).order_by(
                "name"
            )

            for student in students:

                marks = Marks.objects.filter(
                    student=student,
                    subject__in=subjects,
                    entered_by=faculty
                ).select_related(
                    "subject"
                ).order_by(
                    "subject__name",
                    "exam_name"
                )

                student_data.append({
                    "student": student,
                    "marks": marks,
                })

    context = {
        "faculty": faculty,
        "years": years,
        "semesters": semesters,
        "selected_year": selected_year,
        "selected_semester": selected_semester,
        "students": students,
        "subjects": subjects,
        "student_data": student_data,
        "exam_choices": Marks.EXAM_CHOICES,
    }

    return render(
        request,
        "faculty/marks.html",
        context
    )


@login_required
def faculty_mark_add(request, student_id):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    student = get_object_or_404(
        Student.objects.select_related("user", "department"),
        id=student_id,
        department=faculty.department
    )

    selected_year = request.GET.get(
        "year"
    ) or request.POST.get(
        "year"
    )

    selected_semester = request.GET.get(
        "semester"
    ) or request.POST.get(
        "semester"
    )

    subjects = Subject.objects.filter(
        faculty=faculty,
        year=student.year
    ).select_related(
        "department"
    ).order_by(
        "semester",
        "name"
    )

    if selected_semester:
        try:
            subjects = subjects.filter(
                semester=int(selected_semester)
            )
        except ValueError:
            selected_semester = ""

    if request.method == "POST":

        subject_id = request.POST.get("subject")
        exam_name = request.POST.get("exam_name")
        marks_value = request.POST.get("marks")

        if not subject_id or not exam_name or marks_value == "":
            messages.error(
                request,
                "Please fill all required fields."
            )

            return redirect(
                f"/faculty/marks/{student.id}/add/"
                f"?year={selected_year}"
                f"&semester={selected_semester}"
            )

        try:
            subject = subjects.get(
                id=subject_id
            )
        except Subject.DoesNotExist:

            messages.error(
                request,
                "Invalid subject selected."
            )

            return redirect(
                "faculty-mark-add",
                student_id=student.id
            )

        valid_exam_types = [
            choice[0]
            for choice in Marks.EXAM_CHOICES
        ]

        if exam_name not in valid_exam_types:
            messages.error(
                request,
                "Invalid exam type."
            )

            return redirect(
                "faculty-mark-add",
                student_id=student.id
            )

        try:
            marks_value = float(marks_value)
        except ValueError:

            messages.error(
                request,
                "Marks must be a valid number."
            )

            return redirect(
                "faculty-mark-add",
                student_id=student.id
            )

        if marks_value < 0 or marks_value > 100:

            messages.error(
                request,
                "Marks must be between 0 and 100."
            )

            return redirect(
                "faculty-mark-add",
                student_id=student.id
            )

        if Marks.objects.filter(
            student=student,
            subject=subject,
            exam_name=exam_name
        ).exists():

            messages.error(
                request,
                "Marks already exist for this subject and exam."
            )

            return redirect(
                f"/faculty/marks/{student.id}/add/"
                f"?year={selected_year}"
                f"&semester={selected_semester}"
            )

        Marks.objects.create(
            student=student,
            subject=subject,
            exam_name=exam_name,
            marks=marks_value,
            max_marks=100,
            entered_by=faculty
        )

        messages.success(
            request,
            "Marks added successfully."
        )

        return redirect(
            f"/faculty/marks/"
            f"?year={student.year}"
            f"&semester={subject.semester}"
        )

    context = {
        "faculty": faculty,
        "student": student,
        "subjects": subjects,
        "exam_choices": Marks.EXAM_CHOICES,
        "selected_year": selected_year,
        "selected_semester": selected_semester,
    }

    return render(
        request,
        "faculty/mark_form.html",
        context
    )


@login_required
def faculty_mark_edit(request, mark_id):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    mark = get_object_or_404(
        Marks.objects.select_related(
            "student",
            "student__user",
            "subject"
        ),
        id=mark_id,
        entered_by=faculty
    )

    subjects = Subject.objects.filter(
        faculty=faculty,
        year=mark.student.year,
        semester=mark.subject.semester
    ).order_by("name")

    if request.method == "POST":

        subject_id = request.POST.get("subject")
        exam_name = request.POST.get("exam_name")
        marks_value = request.POST.get("marks")

        try:
            subject = subjects.get(
                id=subject_id
            )
        except Subject.DoesNotExist:

            messages.error(
                request,
                "Invalid subject selected."
            )

            return redirect(
                "faculty-mark-edit",
                mark_id=mark.id
            )

        try:
            marks_value = float(marks_value)
        except (TypeError, ValueError):

            messages.error(
                request,
                "Marks must be a valid number."
            )

            return redirect(
                "faculty-mark-edit",
                mark_id=mark.id
            )

        if marks_value < 0 or marks_value > 100:

            messages.error(
                request,
                "Marks must be between 0 and 100."
            )

            return redirect(
                "faculty-mark-edit",
                mark_id=mark.id
            )

        duplicate = Marks.objects.filter(
            student=mark.student,
            subject=subject,
            exam_name=exam_name
        ).exclude(
            id=mark.id
        ).exists()

        if duplicate:

            messages.error(
                request,
                "Marks already exist for this subject and exam."
            )

            return redirect(
                "faculty-mark-edit",
                mark_id=mark.id
            )

        mark.subject = subject
        mark.exam_name = exam_name
        mark.marks = marks_value
        mark.max_marks = 100

        mark.save()

        messages.success(
            request,
            "Marks updated successfully."
        )

        return redirect(
            f"/faculty/marks/"
            f"?year={mark.student.year}"
            f"&semester={subject.semester}"
        )

    context = {
        "faculty": faculty,
        "mark": mark,
        "student": mark.student,
        "subjects": subjects,
        "exam_choices": Marks.EXAM_CHOICES,
    }

    return render(
        request,
        "faculty/mark_form.html",
        context
    )


@login_required
def faculty_mark_delete(request, mark_id):
    if request.user.role != "FACULTY":
        return redirect("dashboard")

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect("login")

    mark = get_object_or_404(
        Marks,
        id=mark_id,
        entered_by=faculty
    )

    student_year = mark.student.year
    semester = mark.subject.semester

    if request.method == "POST":

        mark.delete()

        messages.success(
            request,
            "Marks deleted successfully."
        )

    return redirect(
        f"/faculty/marks/"
        f"?year={student_year}"
        f"&semester={semester}"
    )
# =========================================================
# PLACEMENT DASHBOARD
# =========================================================


@login_required
def placement_dashboard(request):

    if request.user.role != "PLACEMENT":
        return redirect("dashboard")


    total_companies = Company.objects.count()

    total_drives = PlacementDrive.objects.count()

    open_drives = PlacementDrive.objects.filter(
        status="OPEN"
    ).count()

    total_applications = JobApplication.objects.count()

    selected_students = JobApplication.objects.filter(
        status="SELECTED"
    ).count()

    active_applications = JobApplication.objects.filter(
        status__in=[
            "APPLIED",
            "SHORTLISTED",
            "TEST",
            "INTERVIEW",
        ]
    ).count()


    recent_applications = JobApplication.objects.select_related(
        "student",
        "student__user",
        "placement_drive",
        "placement_drive__company"
    ).order_by(
        "-application_date"
    )[:10]


    context = {

        "total_companies":
            total_companies,

        "total_drives":
            total_drives,

        "open_drives":
            open_drives,

        "total_applications":
            total_applications,

        "selected_students":
            selected_students,

        "active_applications":
            active_applications,

        "recent_applications":
            recent_applications,
    }


    return render(
        request,
        "placement/dashboard.html",
        context
    )


@login_required
def placement_companies(request):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    companies = Company.objects.all().order_by(
        "company_name"
    )

    return render(
        request,
        "placement/companies.html",
        {
            "companies": companies,
        }
    )

@login_required
def placement_company_add(request):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    if request.method == "POST":

        company_name = request.POST.get(
            "company_name",
            ""
        ).strip()

        industry = request.POST.get(
            "industry",
            ""
        ).strip()

        website = request.POST.get(
            "website",
            ""
        ).strip()

        hr_name = request.POST.get(
            "hr_name",
            ""
        ).strip()

        hr_email = request.POST.get(
            "hr_email",
            ""
        ).strip()

        hr_phone = request.POST.get(
            "hr_phone",
            ""
        ).strip()

        # Required field
        if not company_name:
            messages.error(
                request,
                "Company name is required."
            )

            return redirect(
                "placement-company-add"
            )

        # Prevent duplicate company names
        if Company.objects.filter(
            company_name__iexact=company_name
        ).exists():

            messages.error(
                request,
                "This company already exists."
            )

            return redirect(
                "placement-company-add"
            )

        Company.objects.create(
            company_name=company_name,
            industry=industry,
            website=website or None,
            hr_name=hr_name,
            hr_email=hr_email,
            hr_phone=hr_phone,
        )

        messages.success(
            request,
            "Company added successfully."
        )

        return redirect(
            "placement-companies"
        )

    return render(
        request,
        "placement/company_form.html"
    )
@login_required
def placement_company_edit(request, company_id):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    company = get_object_or_404(
        Company,
        id=company_id
    )

    if request.method == "POST":

        company_name = request.POST.get(
            "company_name",
            ""
        ).strip()

        industry = request.POST.get(
            "industry",
            ""
        ).strip()

        website = request.POST.get(
            "website",
            ""
        ).strip()

        hr_name = request.POST.get(
            "hr_name",
            ""
        ).strip()

        hr_email = request.POST.get(
            "hr_email",
            ""
        ).strip()

        hr_phone = request.POST.get(
            "hr_phone",
            ""
        ).strip()

        # Required
        if not company_name:
            messages.error(
                request,
                "Company name is required."
            )

            return render(
                request,
                "placement/company_form.html",
                {
                    "company": company,
                    "page_title": "Edit Company",
                    "button_text": "Save Changes",
                }
            )

        # Duplicate company name check
        if Company.objects.filter(
            company_name__iexact=company_name
        ).exclude(
            id=company.id
        ).exists():

            messages.error(
                request,
                "Another company with this name already exists."
            )

            return render(
                request,
                "placement/company_form.html",
                {
                    "company": company,
                    "page_title": "Edit Company",
                    "button_text": "Save Changes",
                }
            )

        company.company_name = company_name
        company.industry = industry
        company.website = website or None
        company.hr_name = hr_name
        company.hr_email = hr_email
        company.hr_phone = hr_phone

        company.save()

        messages.success(
            request,
            "Company updated successfully."
        )

        return redirect(
            "placement-companies"
        )

    return render(
        request,
        "placement/company_form.html",
        {
            "company": company,
            "page_title": "Edit Company",
            "button_text": "Save Changes",
        }
    )
@login_required
def placement_drives(request):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    drives = PlacementDrive.objects.select_related(
        "company",
        "created_by"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "placement/drives.html",
        {
            "drives": drives,
        }
    )
@login_required
def placement_company_delete(request, company_id):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    company = get_object_or_404(
        Company,
        id=company_id
    )

    if request.method == "POST":

        # Prevent accidental deletion when drives exist
        if PlacementDrive.objects.filter(
            company=company
        ).exists():

            messages.error(
                request,
                "This company cannot be deleted because placement drives are linked to it."
            )

            return redirect(
                "placement-companies"
            )

        company.delete()

        messages.success(
            request,
            "Company deleted successfully."
        )

    return redirect(
        "placement-companies"
    )

@login_required
def placement_drive_add(request):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    companies = Company.objects.all().order_by(
        "company_name"
    )

    if request.method == "POST":

        company_id = request.POST.get(
            "company"
        )

        job_title = request.POST.get(
            "job_title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        package_value = request.POST.get(
            "package",
            ""
        ).strip()

        location = request.POST.get(
            "location",
            ""
        ).strip()

        minimum_cgpa_value = request.POST.get(
            "minimum_cgpa",
            "0"
        ).strip()

        allowed_departments = request.POST.get(
            "allowed_departments",
            ""
        ).strip()

        maximum_backlogs_value = request.POST.get(
            "maximum_backlogs",
            "0"
        ).strip()

        application_deadline = request.POST.get(
            "application_deadline"
        )

        drive_date = request.POST.get(
            "drive_date"
        )

        status = request.POST.get(
            "status",
            "DRAFT"
        )

        # -----------------------------
        # Required fields
        # -----------------------------

        if not company_id:
            messages.error(
                request,
                "Please select a company."
            )

            return redirect(
                "placement-drive-add"
            )

        if not job_title:
            messages.error(
                request,
                "Job title is required."
            )

            return redirect(
                "placement-drive-add"
            )

        if not description:
            messages.error(
                request,
                "Job description is required."
            )

            return redirect(
                "placement-drive-add"
            )

        if not location:
            messages.error(
                request,
                "Job location is required."
            )

            return redirect(
                "placement-drive-add"
            )

        if not allowed_departments:
            messages.error(
                request,
                "Allowed departments are required."
            )

            return redirect(
                "placement-drive-add"
            )

        if not application_deadline:
            messages.error(
                request,
                "Application deadline is required."
            )

            return redirect(
                "placement-drive-add"
            )

        # -----------------------------
        # Company
        # -----------------------------

        company = get_object_or_404(
            Company,
            id=company_id
        )

        # -----------------------------
        # Package
        # -----------------------------

        try:
            package = Decimal(
                package_value
            )
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Enter a valid package."
            )

            return redirect(
                "placement-drive-add"
            )

        if package < 0:
            messages.error(
                request,
                "Package cannot be negative."
            )

            return redirect(
                "placement-drive-add"
            )

        # -----------------------------
        # Minimum CGPA
        # -----------------------------

        try:
            minimum_cgpa = Decimal(
                minimum_cgpa_value
            )
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Enter a valid minimum CGPA."
            )

            return redirect(
                "placement-drive-add"
            )

        if minimum_cgpa < 0 or minimum_cgpa > 10:

            messages.error(
                request,
                "Minimum CGPA must be between 0 and 10."
            )

            return redirect(
                "placement-drive-add"
            )

        # -----------------------------
        # Maximum backlogs
        # -----------------------------

        try:
            maximum_backlogs = int(
                maximum_backlogs_value
            )
        except (
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Maximum backlogs must be a valid number."
            )

            return redirect(
                "placement-drive-add"
            )

        if maximum_backlogs < 0:

            messages.error(
                request,
                "Maximum backlogs cannot be negative."
            )

            return redirect(
                "placement-drive-add"
            )

        # -----------------------------
        # Status
        # -----------------------------

        valid_statuses = [
            choice[0]
            for choice in PlacementDrive.STATUS_CHOICES
        ]

        if status not in valid_statuses:

            messages.error(
                request,
                "Invalid placement drive status."
            )

            return redirect(
                "placement-drive-add"
            )

        # -----------------------------
        # Date validation
        # -----------------------------

        try:

            application_deadline_date = datetime.strptime(
                application_deadline,
                "%Y-%m-%d"
            ).date()

            drive_date_value = None

            if drive_date:
                drive_date_value = datetime.strptime(
                    drive_date,
                    "%Y-%m-%d"
                ).date()

        except ValueError:

            messages.error(
                request,
                "Please enter valid dates."
            )

            return redirect(
                "placement-drive-add"
            )

        # Drive date should not be before deadline
        if (
            drive_date_value
            and drive_date_value < application_deadline_date
        ):

            messages.error(
                request,
                "Drive date cannot be before the application deadline."
            )

            return redirect(
                "placement-drive-add"
            )

        # -----------------------------
        # Normalize departments
        # -----------------------------

        allowed_departments = ",".join(
            part.strip().upper()
            for part in allowed_departments.split(",")
            if part.strip()
        )

        if not allowed_departments:

            messages.error(
                request,
                "Enter at least one allowed department."
            )

            return redirect(
                "placement-drive-add"
            )

        # -----------------------------
        # Create Placement Drive
        # -----------------------------

        PlacementDrive.objects.create(
            company=company,
            job_title=job_title,
            description=description,
            package=package,
            location=location,
            minimum_cgpa=minimum_cgpa,
            allowed_departments=allowed_departments,
            maximum_backlogs=maximum_backlogs,
            application_deadline=application_deadline_date,
            drive_date=drive_date_value,
            status=status,
            created_by=request.user,
        )

        messages.success(
            request,
            "Placement drive added successfully."
        )

        return redirect(
            "placement-drives"
        )

    return render(
        request,
        "placement/drive_form.html",
        {
            "companies": companies,
            "status_choices": PlacementDrive.STATUS_CHOICES,
        }
    )

@login_required
def placement_drive_edit(request, drive_id):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    drive = get_object_or_404(PlacementDrive, id=drive_id)

    companies = Company.objects.all().order_by("company_name")

    if request.method == "POST":

        company_id = request.POST.get("company")
        job_title = request.POST.get("job_title", "").strip()
        description = request.POST.get("description", "").strip()
        package_value = request.POST.get("package", "").strip()
        location = request.POST.get("location", "").strip()
        minimum_cgpa_value = request.POST.get("minimum_cgpa", "0").strip()
        allowed_departments = request.POST.get("allowed_departments", "").strip()
        maximum_backlogs_value = request.POST.get("maximum_backlogs", "0").strip()
        application_deadline = request.POST.get("application_deadline")
        drive_date = request.POST.get("drive_date")
        status = request.POST.get("status", "DRAFT")

        if not company_id or not job_title or not description or not location:
            messages.error(request, "Please fill all required fields.")
            return redirect("placement-drive-edit", drive_id=drive.id)

        company = get_object_or_404(Company, id=company_id)

        try:
            package = Decimal(package_value)
            minimum_cgpa = Decimal(minimum_cgpa_value)
            maximum_backlogs = int(maximum_backlogs_value)
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, "Please enter valid numeric values.")
            return redirect("placement-drive-edit", drive_id=drive.id)

        if package < 0:
            messages.error(request, "Package cannot be negative.")
            return redirect("placement-drive-edit", drive_id=drive.id)

        if minimum_cgpa < 0 or minimum_cgpa > 10:
            messages.error(request, "CGPA must be between 0 and 10.")
            return redirect("placement-drive-edit", drive_id=drive.id)

        if maximum_backlogs < 0:
            messages.error(request, "Backlogs cannot be negative.")
            return redirect("placement-drive-edit", drive_id=drive.id)

        try:
            application_deadline_date = datetime.strptime(
                application_deadline, "%Y-%m-%d"
            ).date()

            drive_date_value = None

            if drive_date:
                drive_date_value = datetime.strptime(
                    drive_date, "%Y-%m-%d"
                ).date()

        except (TypeError, ValueError):
            messages.error(request, "Please enter valid dates.")
            return redirect("placement-drive-edit", drive_id=drive.id)

        if (
            drive_date_value
            and drive_date_value < application_deadline_date
        ):
            messages.error(
                request,
                "Drive date cannot be before the application deadline."
            )
            return redirect("placement-drive-edit", drive_id=drive.id)

        allowed_departments = ",".join(
            part.strip().upper()
            for part in allowed_departments.split(",")
            if part.strip()
        )

        if not allowed_departments:
            messages.error(request, "Allowed departments are required.")
            return redirect("placement-drive-edit", drive_id=drive.id)

        drive.company = company
        drive.job_title = job_title
        drive.description = description
        drive.package = package
        drive.location = location
        drive.minimum_cgpa = minimum_cgpa
        drive.allowed_departments = allowed_departments
        drive.maximum_backlogs = maximum_backlogs
        drive.application_deadline = application_deadline_date
        drive.drive_date = drive_date_value
        drive.status = status

        drive.save()

        messages.success(
            request,
            "Placement drive updated successfully."
        )

        return redirect("placement-drives")

    return render(
        request,
        "placement/drive_form.html",
        {
            "drive": drive,
            "companies": companies,
            "status_choices": PlacementDrive.STATUS_CHOICES,
        }
    )
@login_required
def placement_drive_delete(request, drive_id):
    if request.user.role != "PLACEMENT":
        return redirect("dashboard")

    drive = get_object_or_404(
        PlacementDrive,
        id=drive_id
    )

    if request.method == "POST":
        drive.delete()

        messages.success(
            request,
            "Placement drive deleted successfully."
        )

    return redirect("placement-drives")
# =========================================================
# STUDENT DASHBOARD
# =========================================================

@login_required
def student_dashboard(request):
    if request.user.role != "STUDENT":
        return redirect("dashboard")

    try:
        student = Student.objects.select_related(
            "user",
            "department"
        ).get(
            user=request.user
        )
    except Student.DoesNotExist:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect("login")

    # Subjects for student's department and year
    student_subjects = Subject.objects.filter(
        department=student.department,
        year=student.year
    )

    total_subjects = student_subjects.count()

    # Attendance
    attendance_records = Attendance.objects.filter(
        student=student
    )

    total_attendance = attendance_records.count()

    present_attendance = attendance_records.filter(
        status="PRESENT"
    ).count()

    if total_attendance > 0:
        attendance_percentage = round(
            (present_attendance / total_attendance) * 100,
            2
        )
    else:
        attendance_percentage = 0

    # Marks
    total_marks = Marks.objects.filter(
        student=student
    ).count()

    # Open placement drives
    total_open_placements = PlacementDrive.objects.filter(
        status="OPEN"
    ).count()

    # Student applications
    total_applications = JobApplication.objects.filter(
        student=student
    ).count()

    context = {
        "student": student,

        "total_subjects": total_subjects,

        "total_attendance": total_attendance,
        "present_attendance": present_attendance,
        "attendance_percentage": attendance_percentage,

        "total_marks": total_marks,

        "total_open_placements": total_open_placements,

        "total_applications": total_applications,
    }

    return render(
        request,
        "student/dashboard.html",
        context
    )

def send_password_setup_email(request, user, role_name):
    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = default_token_generator.make_token(user)

    setup_link = request.build_absolute_uri(
        reverse(
            "set-initial-password",
            kwargs={
                "uidb64": uid,
                "token": token,
            }
        )
    )

    send_mail(
        subject="College Portal - Set Your Password",
        message=(
            f"Hello {user.first_name},\n\n"
            f"Your {role_name} account has been created.\n\n"
            f"Username: {user.username}\n\n"
            f"Set your password using this link:\n\n"
            f"{setup_link}\n\n"
            f"After setting your password, you can log in.\n\n"
            f"Regards,\n"
            f"College Portal Admin"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return setup_link

@login_required
def admin_announcement_add(request):

    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    announcements = Announcement.objects.select_related(
        "created_by"
    ).order_by("-created_at")

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        notice_type = request.POST.get(
            "notice_type",
            "GENERAL"
        )

        description = request.POST.get(
            "description",
            ""
        ).strip()

        audience = request.POST.get(
            "audience",
            "ALL"
        )

        event_date = request.POST.get(
            "event_date",
            ""
        ).strip()

        # -----------------------------
        # Required fields
        # -----------------------------

        if not title:
            messages.error(
                request,
                "Announcement title is required."
            )

            return redirect(
                "admin-announcement-add"
            )

        if not description:
            messages.error(
                request,
                "Announcement description is required."
            )

            return redirect(
                "admin-announcement-add"
            )

        # -----------------------------
        # Validate type
        # -----------------------------

        valid_types = [
            choice[0]
            for choice in Announcement.TYPE_CHOICES
        ]

        if notice_type not in valid_types:
            messages.error(
                request,
                "Invalid announcement type."
            )

            return redirect(
                "admin-announcement-add"
            )

        # -----------------------------
        # Validate audience
        # -----------------------------

        valid_audiences = [
            choice[0]
            for choice in Announcement.AUDIENCE_CHOICES
        ]

        if audience not in valid_audiences:
            messages.error(
                request,
                "Invalid announcement audience."
            )

            return redirect(
                "admin-announcement-add"
            )

        # -----------------------------
        # Event date
        # -----------------------------

        event_date_value = None

        if event_date:
            try:
                event_date_value = datetime.strptime(
                    event_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                messages.error(
                    request,
                    "Please enter a valid date."
                )

                return redirect(
                    "admin-announcement-add"
                )

        # -----------------------------
        # Create announcement
        # -----------------------------

        Announcement.objects.create(
            title=title,
            notice_type=notice_type,
            description=description,
            audience=audience,
            event_date=event_date_value,
            created_by=request.user,
        )

        messages.success(
            request,
            "Announcement published successfully."
        )

        return redirect(
            "admin-announcement-add"
        )

    return render(
        request,
        "admin/announcement_form.html",
        {
            "announcements": announcements,
            "notice_types": Announcement.TYPE_CHOICES,
            "audiences": Announcement.AUDIENCE_CHOICES,
        }
    )

@login_required
def admin_announcement_edit(request, announcement_id):

    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    announcement = get_object_or_404(
        Announcement,
        id=announcement_id
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        notice_type = request.POST.get(
            "notice_type",
            "GENERAL"
        )

        description = request.POST.get(
            "description",
            ""
        ).strip()

        audience = request.POST.get(
            "audience",
            "ALL"
        )

        event_date = request.POST.get(
            "event_date",
            ""
        ).strip()

        # -----------------------------
        # Validation
        # -----------------------------

        if not title:
            messages.error(
                request,
                "Announcement title is required."
            )

            return redirect(
                "admin-announcement-edit",
                announcement_id=announcement.id
            )

        if not description:
            messages.error(
                request,
                "Announcement description is required."
            )

            return redirect(
                "admin-announcement-edit",
                announcement_id=announcement.id
            )

        valid_types = [
            choice[0]
            for choice in Announcement.TYPE_CHOICES
        ]

        if notice_type not in valid_types:
            messages.error(
                request,
                "Invalid announcement type."
            )

            return redirect(
                "admin-announcement-edit",
                announcement_id=announcement.id
            )

        valid_audiences = [
            choice[0]
            for choice in Announcement.AUDIENCE_CHOICES
        ]

        if audience not in valid_audiences:
            messages.error(
                request,
                "Invalid announcement audience."
            )

            return redirect(
                "admin-announcement-edit",
                announcement_id=announcement.id
            )

        event_date_value = None

        if event_date:
            try:
                event_date_value = datetime.strptime(
                    event_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                messages.error(
                    request,
                    "Please enter a valid date."
                )

                return redirect(
                    "admin-announcement-edit",
                    announcement_id=announcement.id
                )

        # -----------------------------
        # Update
        # -----------------------------

        announcement.title = title
        announcement.notice_type = notice_type
        announcement.description = description
        announcement.audience = audience
        announcement.event_date = event_date_value

        announcement.save()

        messages.success(
            request,
            "Announcement updated successfully."
        )

        return redirect(
            "admin-announcement-add"
        )

    return render(
        request,
        "admin/announcement_form.html",
        {
            "announcement": announcement,
            "notice_types": Announcement.TYPE_CHOICES,
            "audiences": Announcement.AUDIENCE_CHOICES,
        }
    )
@login_required
def admin_announcement_delete(request, announcement_id):

    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    announcement = get_object_or_404(
        Announcement,
        id=announcement_id
    )

    if request.method == "POST":

        announcement.delete()

        messages.success(
            request,
            "Announcement deleted successfully."
        )

    return redirect(
        "admin-announcement-add"
    )
# =========================================================
# HTML HOLIDAY MANAGEMENT
# =========================================================

@login_required
def admin_holiday_manage(request):

    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    holidays = Holiday.objects.select_related(
        "created_by"
    ).order_by("date")

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        date_value = request.POST.get(
            "date",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        if not title:
            messages.error(
                request,
                "Holiday title is required."
            )

            return redirect(
                "admin-holiday-manage"
            )

        if not date_value:
            messages.error(
                request,
                "Holiday date is required."
            )

            return redirect(
                "admin-holiday-manage"
            )

        Holiday.objects.create(
            title=title,
            date=date_value,
            description=description,
            created_by=request.user,
        )

        messages.success(
            request,
            "Holiday added successfully."
        )

        return redirect(
            "admin-holiday-manage"
        )

    return render(
        request,
        "admin/holiday_form.html",
        {
            "holidays": holidays,
        }
    )
@login_required
def admin_holiday_edit(
    request,
    holiday_id
):

    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    holiday = get_object_or_404(
        Holiday,
        id=holiday_id
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        date_value = request.POST.get(
            "date",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        if not title:
            messages.error(
                request,
                "Holiday title is required."
            )

            return redirect(
                "admin-holiday-edit",
                holiday_id=holiday.id
            )

        if not date_value:
            messages.error(
                request,
                "Holiday date is required."
            )

            return redirect(
                "admin-holiday-edit",
                holiday_id=holiday.id
            )

        holiday.title = title
        holiday.date = date_value
        holiday.description = description

        holiday.save()

        messages.success(
            request,
            "Holiday updated successfully."
        )

        return redirect(
            "admin-holiday-manage"
        )

    return render(
        request,
        "admin/holiday_form.html",
        {
            "holiday": holiday,
            "holidays": Holiday.objects.select_related(
                "created_by"
            ).order_by("date"),
        }
    )

@login_required
def admin_holiday_delete(
    request,
    holiday_id
):

    if not (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):
        return redirect("dashboard")

    holiday = get_object_or_404(
        Holiday,
        id=holiday_id
    )

    if request.method == "POST":

        holiday.delete()

        messages.success(
            request,
            "Holiday deleted successfully."
        )

    return redirect(
        "admin-holiday-manage"
    )

# =========================================================
# USER ANNOUNCEMENTS + HOLIDAYS
# FACULTY / STUDENT / PLACEMENT
# READ ONLY
# =========================================================

@login_required
def user_announcements(request):

    role = request.user.role

    # Only these roles can access this page
    if role not in ["FACULTY", "STUDENT", "PLACEMENT"]:
        return redirect("dashboard")

    # -----------------------------------------
    # Announcement filtering by role
    # -----------------------------------------

    if role == "FACULTY":

        announcements = Announcement.objects.filter(
            audience__in=["ALL", "FACULTY"]
        ).order_by("-created_at")

    elif role == "STUDENT":

        announcements = Announcement.objects.filter(
            audience__in=["ALL", "STUDENT"]
        ).order_by("-created_at")

    else:  # PLACEMENT

        announcements = Announcement.objects.filter(
            audience__in=["ALL", "PLACEMENT"]
        ).order_by("-created_at")

    # -----------------------------------------
    # Holidays
    # Everyone can see all holidays
    # -----------------------------------------

    holidays = Holiday.objects.all().order_by("date")

    context = {
        "announcements": announcements,
        "holidays": holidays,
        "role": role,
    }

    return render(
        request,
        "notifications/announcements.html",
        context
    )
# =========================================================
# STUDENT ATTENDANCE
# =========================================================

@login_required
def student_attendance(request):

    if request.user.role != "STUDENT":
        return redirect("dashboard")

    try:
        student = Student.objects.select_related(
            "user",
            "department"
        ).get(
            user=request.user
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect("login")


    # =====================================================
    # YEAR / MONTH SELECTION
    # =====================================================

    today = timezone.localdate()

    selected_year = request.GET.get(
        "year",
        str(today.year)
    )

    selected_month = request.GET.get(
        "month",
        str(today.month)
    )


    try:
        selected_year = int(selected_year)
    except (TypeError, ValueError):
        selected_year = today.year


    try:
        selected_month = int(selected_month)
    except (TypeError, ValueError):
        selected_month = today.month


    # Valid month
    if selected_month < 1 or selected_month > 12:
        selected_month = today.month


    # =====================================================
    # YEAR OPTIONS
    # =====================================================

    current_year = today.year

    years = list(
        range(
            current_year - 5,
            current_year + 2
        )
    )


    # =====================================================
    # MONTH OPTIONS
    # =====================================================

    months = [
        {
            "number": 1,
            "name": "January"
        },
        {
            "number": 2,
            "name": "February"
        },
        {
            "number": 3,
            "name": "March"
        },
        {
            "number": 4,
            "name": "April"
        },
        {
            "number": 5,
            "name": "May"
        },
        {
            "number": 6,
            "name": "June"
        },
        {
            "number": 7,
            "name": "July"
        },
        {
            "number": 8,
            "name": "August"
        },
        {
            "number": 9,
            "name": "September"
        },
        {
            "number": 10,
            "name": "October"
        },
        {
            "number": 11,
            "name": "November"
        },
        {
            "number": 12,
            "name": "December"
        },
    ]


    # =====================================================
    # MONTH NAME
    # =====================================================

    month_name = months[selected_month - 1]["name"]


    # =====================================================
    # ATTENDANCE RECORDS
    # =====================================================

    attendance_records = Attendance.objects.filter(
        student=student,
        date__year=selected_year,
        date__month=selected_month
    ).order_by("date")


    # =====================================================
    # DAILY DATA
    # =====================================================

    daily_data = {}


    for record in attendance_records:

        date_value = record.date

        if date_value not in daily_data:

            daily_data[date_value] = {
                "present": 0,
                "absent": 0,
                "total": 0,
            }


        if record.status == "PRESENT":

            daily_data[date_value]["present"] += 1

        elif record.status == "ABSENT":

            daily_data[date_value]["absent"] += 1


        daily_data[date_value]["total"] += 1


    # =====================================================
    # MONTHLY TOTALS
    # =====================================================

    total_present = attendance_records.filter(
        status="PRESENT"
    ).count()


    total_absent = attendance_records.filter(
        status="ABSENT"
    ).count()


    total_classes = attendance_records.count()


    if total_classes > 0:

        monthly_percentage = round(
            (total_present / total_classes) * 100,
            2
        )

    else:

        monthly_percentage = 0


    # =====================================================
    # DAY-WISE REPORT
    # =====================================================

    import calendar

    number_of_days = calendar.monthrange(
        selected_year,
        selected_month
    )[1]


    daily_rows = []


    for day in range(
        1,
        number_of_days + 1
    ):

        day_date = datetime(
            selected_year,
            selected_month,
            day
        ).date()


        record = daily_data.get(
            day_date
        )


        if record:

            present = record["present"]
            absent = record["absent"]
            total = record["total"]

            percentage = round(
                (present / total) * 100,
                2
            ) if total > 0 else 0

            daily_rows.append({

                "date": day_date,

                "day_name": day_date.strftime(
                    "%A"
                ),

                "present": present,

                "absent": absent,

                "total": total,

                "percentage": percentage,

                "has_class": True,

            })

        else:

            daily_rows.append({

                "date": day_date,

                "day_name": day_date.strftime(
                    "%A"
                ),

                "present": 0,

                "absent": 0,

                "total": 0,

                "percentage": 0,

                "has_class": False,

            })


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "student": student,

        "years": years,

        "months": months,

        "selected_year": selected_year,

        "selected_month": selected_month,

        "month_name": month_name,

        "daily_rows": daily_rows,

        "total_present": total_present,

        "total_absent": total_absent,

        "total_classes": total_classes,

        "monthly_percentage": monthly_percentage,

    }


    return render(
        request,
        "student/attendance.html",
        context
    )
# =========================================================
# STUDENT MARKS
# =========================================================

@login_required
def student_marks(request):

    if request.user.role != "STUDENT":
        return redirect("dashboard")

    try:
        student = Student.objects.select_related(
            "user",
            "department"
        ).get(
            user=request.user
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect("login")


    # =====================================================
    # YEAR / SEMESTER
    # =====================================================

    selected_year = request.GET.get("year", "")
    selected_semester = request.GET.get("semester", "")

    try:
        selected_year = int(selected_year)
    except (TypeError, ValueError):
        selected_year = None

    try:
        selected_semester = int(selected_semester)
    except (TypeError, ValueError):
        selected_semester = None


    years = [1, 2, 3, 4]
    semesters = [1, 2, 3, 4, 5, 6, 7, 8]


    subject_rows = []

    overall_total = 0
    overall_max = 0


    # =====================================================
    # LOAD MARKS ONLY AFTER YEAR + SEMESTER
    # =====================================================

    if selected_year and selected_semester:

        subjects = Subject.objects.filter(
            department=student.department,
            year=selected_year,
            semester=selected_semester
        ).order_by(
            "code",
            "name"
        )


        marks = Marks.objects.filter(
            student=student,
            subject__department=student.department,
            subject__year=selected_year,
            subject__semester=selected_semester
        ).select_related(
            "subject"
        ).order_by(
            "subject__code"
        )


        # -------------------------------------------------
        # Group marks subject-wise
        # -------------------------------------------------

        marks_by_subject = {}

        for mark in marks:

            subject_id = mark.subject_id

            if subject_id not in marks_by_subject:

                marks_by_subject[subject_id] = {
                    "INTERNAL_1": 0,
                    "INTERNAL_2": 0,
                    "ASSIGNMENT": 0,
                    "MID_EXAM": 0,
                }

            marks_by_subject[subject_id][
                mark.exam_name
            ] = mark.marks


        # -------------------------------------------------
        # Build subject rows
        # -------------------------------------------------

        for subject in subjects:

            subject_marks = marks_by_subject.get(
                subject.id,
                {}
            )


            internal_1 = subject_marks.get(
                "INTERNAL_1",
                0
            )

            internal_2 = subject_marks.get(
                "INTERNAL_2",
                0
            )

            assignment = subject_marks.get(
                "ASSIGNMENT",
                0
            )

            mid_exam = subject_marks.get(
                "MID_EXAM",
                0
            )


            total_marks = (
                internal_1
                + internal_2
                + assignment
                + mid_exam
            )


            max_marks = 400


            percentage = (
                round(
                    (float(total_marks) / max_marks) * 100,
                    2
                )
                if max_marks > 0
                else 0
            )


            subject_rows.append({

                "subject": subject,

                "internal_1": internal_1,

                "internal_2": internal_2,

                "assignment": assignment,

                "mid_exam": mid_exam,

                "total": total_marks,

                "max_marks": max_marks,

                "percentage": percentage,

            })


            overall_total += total_marks
            overall_max += max_marks


    # =====================================================
    # OVERALL PERCENTAGE
    # =====================================================

    if overall_max > 0:

        overall_percentage = round(
            (float(overall_total) / overall_max) * 100,
            2
        )

    else:

        overall_percentage = 0


    context = {

        "student": student,

        "college_name":
            "JNTUA College of Engineering, Pulivendula",

        "years": years,

        "semesters": semesters,

        "selected_year": selected_year,

        "selected_semester": selected_semester,

        "subject_rows": subject_rows,

        "overall_total": overall_total,

        "overall_max": overall_max,

        "overall_percentage": overall_percentage,

    }


    return render(
        request,
        "student/marks.html",
        context
    )

# =========================================================
# STUDENT - PLACEMENTS
# =========================================================

# =========================================================
# STUDENT - PLACEMENTS
# =========================================================

@login_required
def student_placements(request):

    if request.user.role != "STUDENT":
        return redirect("dashboard")

    try:
        student = Student.objects.select_related(
            "user",
            "department"
        ).get(
            user=request.user
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect("login")


    today = timezone.localdate()


    # =====================================================
    # GET ALL OPEN DRIVES
    # =====================================================

    drives = PlacementDrive.objects.select_related(
        "company"
    ).filter(
        status="OPEN"
    ).order_by(
        "application_deadline"
    )


    # =====================================================
    # ALREADY APPLIED DRIVES
    # =====================================================

    applied_drive_ids = set(
        JobApplication.objects.filter(
            student=student
        ).values_list(
            "placement_drive_id",
            flat=True
        )
    )


    # =====================================================
    # STUDENT DEPARTMENT VALUES
    # Match BOTH name and code
    # =====================================================

    student_department_name = (
        student.department.name or ""
    ).strip().upper()

    student_department_code = (
        student.department.code or ""
    ).strip().upper()


    # =====================================================
    # CHECK EACH DRIVE
    # =====================================================

    for drive in drives:

        allowed_departments = [
            item.strip().upper()
            for item in drive.allowed_departments.split(",")
            if item.strip()
        ]


        # ---------------------------------------------
        # Department eligibility
        # ---------------------------------------------

        department_eligible = (
            student_department_name in allowed_departments
            or
            student_department_code in allowed_departments
        )


        # ---------------------------------------------
        # CGPA eligibility
        # ---------------------------------------------

        cgpa_eligible = (
            student.cgpa >= drive.minimum_cgpa
        )


        # ---------------------------------------------
        # Deadline eligibility
        # ---------------------------------------------

        deadline_valid = (
            drive.application_deadline >= today
        )


        # ---------------------------------------------
        # Final eligibility
        # ---------------------------------------------

        drive.is_eligible = (
            department_eligible
            and cgpa_eligible
            and deadline_valid
        )


        drive.department_eligible = department_eligible

        drive.cgpa_eligible = cgpa_eligible

        drive.deadline_valid = deadline_valid


        drive.already_applied = (
            drive.id in applied_drive_ids
        )


    context = {

        "student": student,

        "drives": drives,

        "applied_drive_ids":
            applied_drive_ids,

        "today": today,

    }


    return render(
        request,
        "student/placements.html",
        context
    )
# =========================================================
# STUDENT - APPLY FOR PLACEMENT
# =========================================================

# =========================================================
# STUDENT - APPLY FOR PLACEMENT
# =========================================================

@login_required
def student_apply_placement(request, drive_id):

    if request.user.role != "STUDENT":
        return redirect("dashboard")

    if request.method != "POST":
        return redirect("student-placements")

    try:
        student = Student.objects.select_related(
            "department"
        ).get(
            user=request.user
        )
    except Student.DoesNotExist:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect("login")

    drive = get_object_or_404(
        PlacementDrive,
        id=drive_id
    )

    # Check drive status
    if drive.status != "OPEN":
        messages.error(
            request,
            "This placement drive is not open."
        )
        return redirect("student-placements")

    # Check deadline
    today = timezone.localdate()

    if drive.application_deadline < today:
        messages.error(
            request,
            "The application deadline has passed."
        )
        return redirect("student-placements")

    # Department eligibility
    allowed_departments = [
        item.strip().upper()
        for item in drive.allowed_departments.split(",")
        if item.strip()
    ]

    student_department_name = (
        student.department.name or ""
    ).strip().upper()

    student_department_code = (
        student.department.code or ""
    ).strip().upper()

    department_eligible = (
        student_department_name in allowed_departments
        or
        student_department_code in allowed_departments
    )

    if not department_eligible:
        messages.error(
            request,
            "You are not eligible for this placement drive."
        )
        return redirect("student-placements")

    # CGPA eligibility
    if student.cgpa < drive.minimum_cgpa:
        messages.error(
            request,
            f"Minimum CGPA required is {drive.minimum_cgpa}. "
            f"Your current CGPA is {student.cgpa}."
        )
        return redirect("student-placements")

    # Prevent duplicate application
    if JobApplication.objects.filter(
        student=student,
        placement_drive=drive
    ).exists():

        messages.warning(
            request,
            "You have already applied for this placement drive."
        )

        return redirect("student-applications")

    # Create application
    JobApplication.objects.create(
        student=student,
        placement_drive=drive,
        status="APPLIED",
    )

    messages.success(
        request,
        f"You successfully applied to "
        f"{drive.company.company_name}."
    )

    return redirect("student-applications")
# =========================================================
# STUDENT - MY APPLICATIONS
# =========================================================

# =========================================================
# STUDENT - MY APPLICATIONS
# =========================================================

@login_required
def student_applications(request):

    if request.user.role != "STUDENT":
        return redirect("dashboard")

    try:
        student = Student.objects.get(
            user=request.user
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect("login")


    applications = JobApplication.objects.select_related(
        "placement_drive",
        "placement_drive__company"
    ).filter(
        student=student
    ).order_by(
        "-application_date"
    )


    return render(
        request,
        "student/applications.html",
        {
            "applications": applications,
        }
    )
# =========================================================
# PLACEMENT CELL - APPLICATIONS
# =========================================================

@login_required
def placement_applications(request):

    if request.user.role != "PLACEMENT":
        return redirect("dashboard")


    applications = JobApplication.objects.select_related(
        "student",
        "student__user",
        "student__department",
        "placement_drive",
        "placement_drive__company"
    ).order_by(
        "-application_date"
    )


    return render(
        request,
        "placement/applications.html",
        {
            "applications": applications,
            "status_choices": JobApplication.STATUS_CHOICES,
        }
    )
# =========================================================
# PLACEMENT CELL - UPDATE APPLICATION STATUS
# =========================================================

@login_required
def placement_application_status_update(
    request,
    application_id
):

    if request.user.role != "PLACEMENT":
        return redirect("dashboard")


    application = get_object_or_404(
        JobApplication,
        id=application_id
    )


    if request.method == "POST":

        new_status = request.POST.get(
            "status",
            ""
        )


        valid_statuses = [
            choice[0]
            for choice in JobApplication.STATUS_CHOICES
        ]


        if new_status not in valid_statuses:

            messages.error(
                request,
                "Invalid application status."
            )

            return redirect(
                "placement-applications"
            )


        application.status = new_status

        application.save()


        messages.success(
            request,
            f"Application status updated to {application.get_status_display()}."
        )


    return redirect(
        "placement-applications"
    )