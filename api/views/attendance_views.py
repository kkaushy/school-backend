from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import Attendance, Student, Staff, User
from ..serializers import AttendanceSerializer, StudentSerializer


class MarkAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Attendance'],
        summary='Mark or clear attendance for a student or staff member',
        request=inline_serializer(
            name='MarkAttendanceRequest',
            fields={
                'userId': drf_serializers.IntegerField(),
                'userType': drf_serializers.ChoiceField(choices=['Student', 'Staff']),
                'date': drf_serializers.DateField(),
                'status': drf_serializers.ChoiceField(choices=['Present', 'Absent', 'Not Marked']),
            },
        ),
        responses={
            200: OpenApiResponse(description='Attendance saved or cleared'),
            400: OpenApiResponse(description='Missing or invalid fields'),
            404: OpenApiResponse(description='Student or staff not found'),
        },
    )
    def post(self, request):
        data = request.data
        user_id = data.get('userId')
        user_type = data.get('userType')
        date = data.get('date')
        attendance_status = data.get('status')

        if not user_id or not user_type or not date:
            return Response({'message': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        if attendance_status == 'Not Marked':
            if user_type == 'Student':
                Attendance.objects.filter(student_id=user_id, user_type='Student', date=date).delete()
            else:
                Attendance.objects.filter(staff_member_id=user_id, user_type='Staff', date=date).delete()
            return Response({'message': 'Attendance cleared'})

        if user_type == 'Student':
            try:
                student = Student.objects.get(pk=user_id)
            except Student.DoesNotExist:
                return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

            Attendance.objects.update_or_create(
                student=student,
                user_type='Student',
                date=date,
                defaults={'status': attendance_status},
            )
        elif user_type == 'Staff':
            try:
                staff = Staff.objects.get(pk=user_id)
            except Staff.DoesNotExist:
                return Response({'message': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)

            Attendance.objects.update_or_create(
                staff_member=staff,
                user_type='Staff',
                date=date,
                defaults={'status': attendance_status},
            )
        else:
            return Response({'message': 'Invalid userType'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Attendance saved'})


class StudentAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Attendance'],
        summary='List student attendance records',
        parameters=[
            OpenApiParameter('className', str, description='Filter by class name'),
            OpenApiParameter('date', str, description='Filter by date (YYYY-MM-DD)'),
        ],
        responses={200: AttendanceSerializer(many=True)},
    )
    def get(self, request):
        class_name = request.query_params.get('className')
        date = request.query_params.get('date')

        queryset = Attendance.objects.filter(user_type='Student').select_related('student').order_by('-date')

        if class_name:
            queryset = queryset.filter(student__class_name=class_name)
        if date:
            queryset = queryset.filter(date=date)

        serializer = AttendanceSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentsByClassView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Attendance'],
        summary='List students filtered by class (for attendance marking)',
        parameters=[
            OpenApiParameter('className', str, description='Filter by class name'),
        ],
        responses={200: StudentSerializer(many=True)},
    )
    def get(self, request):
        class_name = request.query_params.get('className')
        query = {}
        if class_name:
            query['class_name'] = class_name

        students = Student.objects.filter(**query).order_by('name')
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


class StaffAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Attendance'],
        summary='List staff attendance records',
        parameters=[
            OpenApiParameter('date', str, description='Filter by date (YYYY-MM-DD)'),
        ],
        responses={200: AttendanceSerializer(many=True)},
    )
    def get(self, request):
        date = request.query_params.get('date')
        queryset = Attendance.objects.filter(user_type='Staff').select_related('staff_member').order_by('-date')

        if date:
            queryset = queryset.filter(date=date)

        serializer = AttendanceSerializer(queryset, many=True)
        return Response(serializer.data)


class ParentStudentAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Attendance'],
        summary='Get attendance summary for a parent\'s linked student',
        responses={
            200: inline_serializer(
                name='ParentAttendanceResponse',
                fields={
                    'student': StudentSerializer(),
                    'attendance': AttendanceSerializer(many=True),
                    'summary': inline_serializer(
                        name='AttendanceSummary',
                        fields={
                            'totalDays': drf_serializers.IntegerField(),
                            'presentDays': drf_serializers.IntegerField(),
                            'absentDays': drf_serializers.IntegerField(),
                            'attendancePercentage': drf_serializers.FloatField(),
                        },
                    ),
                },
            ),
            404: OpenApiResponse(description='No student linked to this parent'),
        },
    )
    def get(self, request, parent_id):
        student = Student.objects.filter(parent_id=parent_id).first()
        if not student:
            return Response({'message': 'No student linked to this parent'}, status=status.HTTP_404_NOT_FOUND)

        attendance = Attendance.objects.filter(
            student=student,
            user_type='Student',
        ).order_by('-date')

        total_days = attendance.count()
        present_days = attendance.filter(status='Present').count()
        absent_days = attendance.filter(status='Absent').count()
        attendance_percentage = round((present_days / total_days) * 100, 1) if total_days > 0 else 0

        return Response({
            'student': StudentSerializer(student).data,
            'attendance': AttendanceSerializer(attendance, many=True).data,
            'summary': {
                'totalDays': total_days,
                'presentDays': present_days,
                'absentDays': absent_days,
                'attendancePercentage': attendance_percentage,
            },
        })
