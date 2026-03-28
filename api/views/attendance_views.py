from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from ..models import Student, Attendance
from ..permissions import require_roles
from classes.models import Class, ClassStudent


class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        class_id = request.query_params.get('class_id')
        date = request.query_params.get('date')
        if not class_id or not date:
            return Response({'message': 'class_id and date are required'}, status=status.HTTP_400_BAD_REQUEST)
        student_ids = ClassStudent.objects.filter(class_ref_id=class_id).values_list('student_id', flat=True)
        students = Student.objects.filter(id__in=student_ids)
        attendance_map = {
            a.student_id: a
            for a in Attendance.objects.filter(class_ref_id=class_id, date=date, student_id__in=student_ids)
        }
        result = [
            {
                'student_id': str(s.id),
                'student_name': s.name,
                'attendance_status': attendance_map[s.id].status if s.id in attendance_map else None,
                'attendance_id': str(attendance_map[s.id].id) if s.id in attendance_map else None,
            }
            for s in students
        ]
        return Response(result)

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def post(self, request):
        class_id = request.data.get('class_id')
        date = request.data.get('date')
        records = request.data.get('records', [])
        if not class_id or not date:
            return Response({'message': 'class_id and date are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cls = Class.objects.get(pk=class_id)
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            for record in records:
                Attendance.objects.update_or_create(
                    student_id=record['student_id'],
                    date=date,
                    class_ref_id=class_id,
                    defaults={'status': record['status'], 'branch': cls.branch},
                )
        return Response({'message': 'Attendance recorded successfully'})
