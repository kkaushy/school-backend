from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('name', 'Admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    contact = models.CharField(max_length=20, blank=True, null=True)

    # Student-specific fields
    class_name = models.CharField(max_length=50, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)

    # Parent linking — points to a student User
    linked_student_user = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parents',
        limit_choices_to={'role': 'student'},
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.role})"


class Student(models.Model):
    GENDER_CHOICES = [
        ('boy', 'Boy'),
        ('girl', 'Girl'),
    ]

    name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=50)
    seat_number = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        limit_choices_to={'role': 'parent'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        unique_together = ('seat_number', 'class_name')

    def __str__(self):
        return f"{self.name} - Class {self.class_name}"


class Staff(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff'
        verbose_name_plural = 'Staff Members'

    def __str__(self):
        return f"{self.name} - {self.designation}"


class Admission(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    student_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    class_applying = models.CharField(max_length=50)
    father_name = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admissions'

    def __str__(self):
        return f"{self.student_name} - {self.class_applying}"


class Attendance(models.Model):
    USER_TYPE_CHOICES = [
        ('Student', 'Student'),
        ('Staff', 'Staff'),
    ]
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attendance_records',
    )
    staff_member = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attendance_records',
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'date'],
                condition=models.Q(user_type='Student'),
                name='unique_student_attendance_per_day',
            ),
            models.UniqueConstraint(
                fields=['staff_member', 'date'],
                condition=models.Q(user_type='Staff'),
                name='unique_staff_attendance_per_day',
            ),
        ]

    def clean(self):
        if self.user_type == 'Student':
            if not self.student_id:
                raise ValidationError('Student attendance requires a student.')
            if self.staff_member_id:
                raise ValidationError('Student attendance cannot reference a staff member.')
        elif self.user_type == 'Staff':
            if not self.staff_member_id:
                raise ValidationError('Staff attendance requires a staff member.')
            if self.student_id:
                raise ValidationError('Staff attendance cannot reference a student.')

    def __str__(self):
        entity = self.student or self.staff_member
        name = str(entity) if entity else 'Unknown'
        return f"{name} - {self.date} - {self.status}"


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contacts'

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Exam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exams')
    subject = models.CharField(max_length=100)
    marks = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    exam_type = models.CharField(max_length=100)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exams'

    def __str__(self):
        return f"{self.student.name} - {self.subject} {self.marks}/{self.max_marks}"


class Fee(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fees'

    def __str__(self):
        return f"{self.student.name} - {self.amount} ({self.status})"
