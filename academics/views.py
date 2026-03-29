from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import AcademicRecord
from .serializers import AcademicRecordSerializer
from api.permissions import require_roles
from api.constants import COMPANY_ADMIN, BRANCH_ADMIN, TEACHER
from branches.models import BranchUser
from classes.models import ClassTeacher, ClassStudent


def get_accessible_records(user):
    if user.is_superuser:
        return AcademicRecord.objects.all()
    if user.role == COMPANY_ADMIN:
        branch_ids = user.branches.values_list('id', flat=True)
        return AcademicRecord.objects.filter(branch_id__in=branch_ids)
    elif user.role == BRANCH_ADMIN:
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        return AcademicRecord.objects.filter(branch_id__in=branch_ids)
    elif user.role == TEACHER:
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        return AcademicRecord.objects.filter(class_ref_id__in=class_ids)
    elif user.role == 'parent':
        student_ids = user.children.values_list('id', flat=True)
        return AcademicRecord.objects.filter(student_id__in=student_ids)
    elif user.role == 'student':
        try:
            return AcademicRecord.objects.filter(student=user.student_profile)
        except Exception:
            return AcademicRecord.objects.none()
    return AcademicRecord.objects.none()


class AcademicRecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = get_accessible_records(request.user)
        return Response(AcademicRecordSerializer(records, many=True).data)

    @require_roles(COMPANY_ADMIN, BRANCH_ADMIN, TEACHER)
    def post(self, request):
        if not request.user.is_superuser:
            # Additional permission checks if needed, but since decorator handles roles, maybe not
            pass
        required = ['student_id', 'class_id', 'term', 'subject_name', 'grade_score']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        cls_id = request.data['class_id']
        from classes.models import Class
        try:
            cls = Class.objects.get(pk=cls_id)
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        record = AcademicRecord.objects.create(
            student_id=request.data['student_id'],
            class_ref_id=cls_id,
            branch=cls.branch,
            term=request.data['term'],
            subject_name=request.data['subject_name'],
            grade_score=request.data['grade_score'],
            remarks=request.data.get('remarks'),
        )
        return Response(AcademicRecordSerializer(record).data, status=status.HTTP_201_CREATED)
