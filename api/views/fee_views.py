from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Student, Fee
from ..serializers import StudentSerializer


class StudentsByClassFeeView(APIView):
    @extend_schema(
        tags=['Fees'],
        summary='List students in a class (for fee management)',
        responses={200: StudentSerializer(many=True)},
    )
    def get(self, request, class_name):
        students = Student.objects.filter(class_name=str(class_name))

        if not students.exists():
            return Response([])

        return Response(StudentSerializer(students, many=True).data)


class StudentFeesView(APIView):
    @extend_schema(
        tags=['Fees'],
        summary='Get fee summary for a student',
        responses={
            200: inline_serializer(
                name='FeeSummaryResponse',
                fields={
                    'totalFees': drf_serializers.DecimalField(max_digits=10, decimal_places=2),
                    'paidFees': drf_serializers.DecimalField(max_digits=10, decimal_places=2),
                    'pendingFees': drf_serializers.DecimalField(max_digits=10, decimal_places=2),
                },
            ),
            404: OpenApiResponse(description='Student not found'),
        },
    )
    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        fees = Fee.objects.filter(student=student)

        total_fees = 0
        paid_fees = 0
        pending_fees = 0

        for f in fees:
            total_fees += f.amount
            if f.status == 'Paid':
                paid_fees += f.amount
            else:
                pending_fees += f.amount

        return Response({
            'totalFees': total_fees,
            'paidFees': paid_fees,
            'pendingFees': pending_fees,
        })
