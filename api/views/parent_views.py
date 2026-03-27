from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import User, Student, Exam, Fee
from ..serializers import ExamSerializer, FeeSerializer, StudentSerializer


class ParentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Parent'],
        summary='Get parent dashboard (linked student\'s exams and fees)',
        responses={
            200: inline_serializer(
                name='ParentDashboardResponse',
                fields={
                    'student': inline_serializer(
                        name='LinkedStudent',
                        fields={
                            'name': drf_serializers.CharField(),
                            'className': drf_serializers.CharField(),
                        },
                    ),
                    'exams': ExamSerializer(many=True),
                    'fees': inline_serializer(
                        name='FeesSummary',
                        fields={
                            'totalFees': drf_serializers.DecimalField(max_digits=10, decimal_places=2),
                            'paidFees': drf_serializers.DecimalField(max_digits=10, decimal_places=2),
                            'pendingFees': drf_serializers.DecimalField(max_digits=10, decimal_places=2),
                        },
                    ),
                },
            ),
            404: OpenApiResponse(description='Parent not found or no student linked'),
        },
    )
    def get(self, request):
        user = request.user

        if user.role != 'parent':
            return Response({'message': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)

        student_user = user.linked_student_user
        if not student_user:
            return Response({'message': 'No student linked'}, status=status.HTTP_404_NOT_FOUND)

        student_record = None
        if student_user.roll_number and student_user.class_name:
            student_record = Student.objects.filter(
                class_name=student_user.class_name,
            ).first()

        exams = []
        fees_summary = {'totalFees': 0, 'paidFees': 0, 'pendingFees': 0}

        if student_record:
            exams = Exam.objects.filter(student=student_record).order_by('-created_at')
            all_fees = Fee.objects.filter(student=student_record)
            total = sum(f.amount for f in all_fees)
            paid = sum(f.amount for f in all_fees if f.status == 'Paid')
            fees_summary = {
                'totalFees': total,
                'paidFees': paid,
                'pendingFees': total - paid,
            }

        return Response({
            'student': {
                'name': student_user.name,
                'className': student_user.class_name,
            },
            'exams': ExamSerializer(exams, many=True).data,
            'fees': fees_summary,
        })
