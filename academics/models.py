from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# =========================================================
# DEPARTMENT
# =========================================================

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# =========================================================
# STUDENT
# =========================================================

class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    student_id = models.CharField(
        max_length=30,
        unique=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="students",
    )

    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ]
    )

    section = models.CharField(max_length=10)

    batch = models.CharField(max_length=20)

    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ]
    )

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


# =========================================================
# FACULTY
# =========================================================

class Faculty(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="faculty_profile",
    )

    faculty_id = models.CharField(
        max_length=30,
        unique=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="faculty_members",
    )

    designation = models.CharField(
        max_length=100,
        blank=True,
    )

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"


# =========================================================
# SUBJECT
# =========================================================

class Subject(models.Model):
    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=30,
        unique=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="subjects",
    )

    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ]
    )

    semester = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8),
        ]
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name="subjects",
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


# =========================================================
# ATTENDANCE
# =========================================================

class Attendance(models.Model):

    STATUS_CHOICES = (
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
    )

    marked_by = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name="attendance_marked",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "subject",
                    "date",
                ],
                name="unique_student_subject_date_attendance",
            )
        ]

        ordering = ["-date"]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.subject.code} - "
            f"{self.date} - "
            f"{self.status}"
        )


# =========================================================
# MARKS
# =========================================================

class Marks(models.Model):

    EXAM_CHOICES = (
        ("INTERNAL_1", "Internal 1"),
        ("INTERNAL_2", "Internal 2"),
        ("ASSIGNMENT", "Assignment"),
        ("MID_EXAM", "Mid Exam"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="marks_records",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="marks_records",
    )

    exam_name = models.CharField(
        max_length=30,
        choices=EXAM_CHOICES,
    )

    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ]
    )

    max_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        validators=[
            MinValueValidator(1),
        ]
    )

    entered_by = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name="marks_entered",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "subject",
                    "exam_name",
                ],
                name="unique_student_subject_exam",
            )
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.subject.code} - "
            f"{self.exam_name}"
        )