from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Class, ClassStudent, ClassTeacher
from .serializers import ClassSerializer
from api.permissions import require_roles
from branches.models import BranchUser


def get_accessible_classes(user):
    if user.role == 'company_admin':
        branch_ids = user.branches.values_list('id', flat=True)
        return Class.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'branch_admin':
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        return Class.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'teacher':
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        return Class.objects.filter(id__in=class_ids)
    return Class.objects.none()


class ClassListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classes = get_accessible_classes(request.user)
        return Response(ClassSerializer(classes, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        name = request.data.get('name')
        branch_id = request.data.get('branch_id')
        if not name or not branch_id:
            return Response({'message': 'name and branch_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        cls = Class.objects.create(name=name, branch_id=branch_id)
        return Response(ClassSerializer(cls).data, status=status.HTTP_201_CREATED)


class ClassDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            cls = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        cls.delete()
        return Response({'message': 'Class deleted successfully'})


class AssignTeacherView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        class_id = request.data.get('class_id')
        teacher_id = request.data.get('teacher_id')
        if not class_id or not teacher_id:
            return Response({'message': 'class_id and teacher_id required'}, status=status.HTTP_400_BAD_REQUEST)
        ClassTeacher.objects.get_or_create(class_ref_id=class_id, teacher_id=teacher_id)
        return Response({'message': 'Teacher assigned successfully'})


class AssignStudentView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def post(self, request):
        class_id = request.data.get('class_id')
        student_id = request.data.get('student_id')
        if not class_id or not student_id:
            return Response({'message': 'class_id and student_id required'}, status=status.HTTP_400_BAD_REQUEST)
        ClassStudent.objects.get_or_create(class_ref_id=class_id, student_id=student_id)
        return Response({'message': 'Student assigned successfully'})
