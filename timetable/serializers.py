from rest_framework import serializers
from .models import TimetableSlot


class TimetableSlotSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_ref.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True, default=None)
    teacher_designation = serializers.CharField(source='teacher.designation', read_only=True, default=None)

    class Meta:
        model = TimetableSlot
        fields = ['id', 'class_ref_id', 'class_name', 'branch_id', 'branch_name',
                  'day_of_week', 'start_time', 'end_time', 'subject_name',
                  'teacher_id', 'teacher_name', 'teacher_designation', 'room', 'created_at']
