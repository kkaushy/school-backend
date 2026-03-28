from rest_framework import serializers
from .models import User, Student, Attendance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'designation', 'avatar_url', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)

    class Meta:
        model = Student
        fields = ['id', 'name', 'branch_id', 'branch_name', 'parent_id', 'parent_name', 'enrollment_date', 'created_at']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'student_id', 'class_ref_id', 'branch_id', 'date', 'status', 'created_at']
