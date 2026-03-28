from django.contrib import admin
from .models import Class, ClassStudent, ClassTeacher


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch']
    search_fields = ['name']
    list_filter = ['branch']


@admin.register(ClassStudent)
class ClassStudentAdmin(admin.ModelAdmin):
    list_display = ['class_ref', 'student']
    list_filter = ['class_ref']


@admin.register(ClassTeacher)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ['class_ref', 'teacher']
    list_filter = ['class_ref']
