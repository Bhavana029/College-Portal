from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


# =========================================================
# COMPANY
# =========================================================

class Company(models.Model):
    company_name = models.CharField(
        max_length=150
    )

    industry = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    hr_name = models.CharField(
        max_length=100,
        blank=True
    )

    hr_email = models.EmailField(
        blank=True
    )

    hr_phone = models.CharField(
        max_length=15,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.company_name


# =========================================================
# PLACEMENT DRIVE
# =========================================================

class PlacementDrive(models.Model):

    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="placement_drives"
    )

    job_title = models.CharField(
        max_length=150
    )

    description = models.TextField()

    package = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    location = models.CharField(
        max_length=150
    )

    minimum_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[
            MinValueValidator(0)
        ]
    )

    allowed_departments = models.CharField(
        max_length=300,
        help_text="Example: CSE,ECE,EEE"
    )

    maximum_backlogs = models.PositiveIntegerField(
        default=0
    )

    application_deadline = models.DateField()

    drive_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="placement_drives_created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.company_name} - {self.job_title}"


# =========================================================
# JOB APPLICATION
# =========================================================

class JobApplication(models.Model):

    STATUS_CHOICES = (
        ("APPLIED", "Applied"),
        ("SHORTLISTED", "Shortlisted"),
        ("TEST", "Test"),
        ("INTERVIEW", "Interview"),
        ("SELECTED", "Selected"),
        ("REJECTED", "Rejected"),
        ("WITHDRAWN", "Withdrawn"),
    )

    student = models.ForeignKey(
        "academics.Student",
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    placement_drive = models.ForeignKey(
        PlacementDrive,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="APPLIED"
    )

    application_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-application_date"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "placement_drive"
                ],
                name="unique_student_placement_application"
            )
        ]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.placement_drive.job_title}"
        )