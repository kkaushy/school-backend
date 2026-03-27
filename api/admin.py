from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Staff, Admission, Attendance, Contact, Exam, Fee


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['name', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['name', 'email']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'role', 'contact', 'class_name', 'roll_number', 'linked_student_user')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_name', 'seat_number', 'gender']
    list_filter = ['class_name', 'gender']
    search_fields = ['name']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'email', 'phone']
    search_fields = ['name', 'email']


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'class_applying', 'mobile', 'created_at']
    search_fields = ['student_name', 'mobile']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user_type', 'date', 'status']
    list_filter = ['user_type', 'status', 'date']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    search_fields = ['name', 'email']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'marks', 'max_marks', 'exam_type', 'date']
    list_filter = ['exam_type', 'subject']


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'status', 'date']
    list_filter = ['status']
