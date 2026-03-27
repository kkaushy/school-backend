from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import User, Student, Staff, Admission, Attendance, Contact, Exam, Fee


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'contact', 'class_name', 'roll_number', 'linked_student_user', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'class_name', 'seat_number', 'gender', 'parent', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'name', 'designation', 'email', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = [
            'id', 'student_name', 'gender', 'dob', 'class_applying',
            'father_name', 'mother_name', 'mobile', 'email', 'address',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()
    seat_number = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'staff_member', 'user_type', 'date', 'status',
            'student_name', 'student_class', 'seat_number',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_student_name(self, obj):
        if obj.user_type == 'Student' and obj.student:
            return obj.student.name
        if obj.user_type == 'Staff' and obj.staff_member:
            return obj.staff_member.name
        return None

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_student_class(self, obj):
        if obj.user_type == 'Student' and obj.student:
            return obj.student.class_name
        return None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_seat_number(self, obj):
        if obj.user_type == 'Student' and obj.student:
            return obj.student.seat_number
        return None


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'student', 'subject', 'marks', 'max_marks', 'exam_type', 'date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = ['id', 'student', 'amount', 'status', 'date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
