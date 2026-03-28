from django.contrib import admin
from .models import AcademicRecord


@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject_name', 'term', 'grade_score']
    search_fields = ['student__name', 'subject_name']
    list_filter = ['term', 'branch']
