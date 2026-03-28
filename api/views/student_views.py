from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import Student
from ..serializers import StudentSerializer
from ..permissions import require_roles
from branches.models import BranchUser
from classes.models import ClassTeacher, ClassStudent


def _get_admin_branch_ids(user):
    from branches.models import BranchUser
    if user.role == 'company_admin':
        return list(user.branches.values_list('id', flat=True))
    return list(BranchUser.objects.filter(user=user).values_list('branch_id', flat=True))


def get_accessible_students(user):
    if user.role == 'company_admin':
        branch_ids = user.branches.values_list('id', flat=True)
        return Student.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'branch_admin':
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        return Student.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'teacher':
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        student_ids = ClassStudent.objects.filter(class_ref_id__in=class_ids).values_list('student_id', flat=True)
        return Student.objects.filter(id__in=student_ids)
    elif user.role == 'parent':
        return Student.objects.filter(parent=user)
    elif user.role == 'student':
        try:
            return Student.objects.filter(user=user)
        except Exception:
            return Student.objects.none()
    return Student.objects.none()


class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = get_accessible_students(request.user)
        return Response(StudentSerializer(students, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        name = request.data.get('name')
        branch_id = request.data.get('branch_id')
        if not name or not branch_id:
            return Response({'message': 'name and branch_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        admin_branch_ids = set(str(b) for b in _get_admin_branch_ids(request.user))
        if str(branch_id) not in admin_branch_ids:
            return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        student = Student.objects.create(
            name=name,
            branch_id=branch_id,
            parent_id=request.data.get('parent_id'),
        )
        return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        from branches.models import BranchUser
        admin_branch_ids = set(_get_admin_branch_ids(request.user))
        if str(student.branch_id) not in {str(b) for b in admin_branch_ids}:
            return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        student.delete()
        return Response({'message': 'Student deleted successfully'})
