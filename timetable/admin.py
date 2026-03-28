from django.contrib import admin
from .models import TimetableSlot


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ['class_ref', 'day_of_week', 'start_time', 'end_time', 'subject_name', 'teacher']
    list_filter = ['day_of_week', 'branch']
    search_fields = ['subject_name', 'teacher__name']
