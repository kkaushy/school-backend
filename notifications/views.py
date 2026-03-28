from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from .models import Notification, NotificationRecipient
from .serializers import NotificationSerializer
from api.permissions import require_roles
from api.models import User
from branches.models import BranchUser
from classes.models import ClassStudent, ClassTeacher

ROLE_TARGET_MAP = {
    'company_admin': ['company_admin', 'branch_admin', 'teacher', 'parent', 'student'],
    'branch_admin': ['branch_admin', 'teacher', 'parent', 'student'],
    'teacher': ['student', 'branch_admin'],
}


def resolve_recipients(target_roles, target_class_id, target_branch_id):
    user_ids = set()
    if target_class_id:
        student_ids = ClassStudent.objects.filter(class_ref_id=target_class_id).values_list('student__user_id', flat=True)
        user_ids.update(uid for uid in student_ids if uid)
        teacher_ids = ClassTeacher.objects.filter(class_ref_id=target_class_id).values_list('teacher_id', flat=True)
        user_ids.update(teacher_ids)
        from api.models import Student
        parent_ids = Student.objects.filter(
            id__in=ClassStudent.objects.filter(class_ref_id=target_class_id).values_list('student_id', flat=True)
        ).exclude(parent=None).values_list('parent_id', flat=True)
        user_ids.update(parent_ids)
        users = User.objects.filter(id__in=user_ids, role__in=target_roles)
    elif target_branch_id:
        user_ids_in_branch = BranchUser.objects.filter(branch_id=target_branch_id).values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids_in_branch, role__in=target_roles)
    else:
        users = User.objects.filter(role__in=target_roles)
    return users


class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notification_ids = NotificationRecipient.objects.filter(
            user=request.user
        ).values_list('notification_id', flat=True)
        notifications = Notification.objects.filter(id__in=notification_ids).order_by('-created_at')[:100]
        serializer = NotificationSerializer(notifications, many=True, context={'request': request})
        return Response(serializer.data)

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def post(self, request):
        title = request.data.get('title')
        message = request.data.get('message')
        target_roles = request.data.get('target_roles', [])
        if not title or not message or not target_roles:
            return Response({'message': 'title, message, and target_roles are required'}, status=status.HTTP_400_BAD_REQUEST)
        allowed = ROLE_TARGET_MAP.get(request.user.role, [])
        invalid = [r for r in target_roles if r not in allowed]
        if invalid:
            return Response({'message': f'Cannot target roles: {invalid}'}, status=status.HTTP_403_FORBIDDEN)
        target_branch_id = request.data.get('target_branch_id')
        target_class_id = request.data.get('target_class_id')
        with transaction.atomic():
            notification = Notification.objects.create(
                sender=request.user,
                title=title,
                message=message,
                target_roles=target_roles,
                target_branch_id=target_branch_id,
                target_class_id=target_class_id,
            )
            recipients = resolve_recipients(target_roles, target_class_id, target_branch_id)
            NotificationRecipient.objects.bulk_create([
                NotificationRecipient(notification=notification, user=user)
                for user in recipients
            ], ignore_conflicts=True)
        return Response({
            'id': str(notification.id),
            'sender_id': str(request.user.id),
            'title': notification.title,
            'message': notification.message,
            'target_roles': notification.target_roles,
            'target_branch_id': str(target_branch_id) if target_branch_id else None,
            'target_class_id': str(target_class_id) if target_class_id else None,
            'created_at': notification.created_at,
            'recipients_count': recipients.count(),
        }, status=status.HTTP_201_CREATED)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            recipient = NotificationRecipient.objects.get(notification_id=pk, user=request.user)
        except NotificationRecipient.DoesNotExist:
            return Response({'message': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        recipient.is_read = True
        recipient.read_at = timezone.now()
        recipient.save()
        return Response({'message': 'Marked as read'})


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        NotificationRecipient.objects.filter(user=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({'message': 'All marked as read'})
