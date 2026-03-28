from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import TimetableSlot
from .serializers import TimetableSlotSerializer
from api.permissions import require_roles
from branches.models import BranchUser
from classes.models import ClassTeacher, ClassStudent


def _get_admin_branch_ids(user):
    if user.role == 'company_admin':
        return list(user.branches.values_list('id', flat=True))
    return list(BranchUser.objects.filter(user=user).values_list('branch_id', flat=True))


def get_accessible_slots(user, class_id=None):
    if user.role == 'company_admin':
        branch_ids = user.branches.values_list('id', flat=True)
        qs = TimetableSlot.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'branch_admin':
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        qs = TimetableSlot.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'teacher':
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        qs = TimetableSlot.objects.filter(class_ref_id__in=class_ids)
    elif user.role == 'parent':
        student_ids = user.children.values_list('id', flat=True)
        class_ids = ClassStudent.objects.filter(student_id__in=student_ids).values_list('class_ref_id', flat=True)
        qs = TimetableSlot.objects.filter(class_ref_id__in=class_ids)
    elif user.role == 'student':
        try:
            class_ids = ClassStudent.objects.filter(student=user.student_profile).values_list('class_ref_id', flat=True)
            qs = TimetableSlot.objects.filter(class_ref_id__in=class_ids)
        except Exception:
            qs = TimetableSlot.objects.none()
    else:
        qs = TimetableSlot.objects.none()
    if class_id:
        qs = qs.filter(class_ref_id=class_id)
    return qs


class TimetableListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        class_id = request.query_params.get('class_id')
        slots = get_accessible_slots(request.user, class_id)
        return Response(TimetableSlotSerializer(slots, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['class_id', 'day_of_week', 'start_time', 'end_time', 'subject_name']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        from classes.models import Class
        try:
            cls = Class.objects.get(pk=request.data['class_id'])
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        slot = TimetableSlot.objects.create(
            class_ref=cls,
            branch=cls.branch,
            day_of_week=request.data['day_of_week'],
            start_time=request.data['start_time'],
            end_time=request.data['end_time'],
            subject_name=request.data['subject_name'],
            teacher_id=request.data.get('teacher_id'),
            room=request.data.get('room'),
        )
        return Response(TimetableSlotSerializer(slot).data, status=status.HTTP_201_CREATED)


class TimetableDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            slot = TimetableSlot.objects.get(pk=pk)
        except TimetableSlot.DoesNotExist:
            return Response({'message': 'Slot not found'}, status=status.HTTP_404_NOT_FOUND)
        admin_branch_ids = set(str(b) for b in _get_admin_branch_ids(request.user))
        if str(slot.branch_id) not in admin_branch_ids:
            return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        slot.delete()
        return Response({'message': 'Slot removed'})
