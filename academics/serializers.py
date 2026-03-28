from rest_framework import serializers
from .models import AcademicRecord


class AcademicRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    class_name = serializers.CharField(source='class_ref.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = AcademicRecord
        fields = ['id', 'student_id', 'student_name', 'class_ref_id', 'class_name',
                  'branch_id', 'branch_name', 'term', 'subject_name', 'grade_score', 'remarks', 'created_at']
