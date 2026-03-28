from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from ..models import User
from ..serializers import UserSerializer
from ..permissions import require_roles
from branches.models import BranchUser


def _get_admin_branch_ids(user):
    if user.role == 'company_admin':
        return list(user.branches.values_list('id', flat=True))
    return list(BranchUser.objects.filter(user=user).values_list('branch_id', flat=True))


class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def get(self, request):
        user = request.user
        if user.is_superuser:
            users = User.objects.all()
        elif user.role == 'company_admin':
            branch_ids = user.branches.values_list('id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            users = User.objects.filter(id__in=user_ids).exclude(id=user.id)
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            users = User.objects.filter(id__in=user_ids, role__in=['teacher', 'branch_admin'])
        return Response(UserSerializer(users, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['name', 'email', 'password', 'role']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=request.data['email']).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        branch_id = request.data.get('branch_id')
        if not branch_id and request.user.role == 'branch_admin':
            branch_ids = BranchUser.objects.filter(user=request.user).values_list('branch_id', flat=True)
            branch_id = str(branch_ids.first()) if branch_ids else None
        with transaction.atomic():
            new_user = User(
                name=request.data['name'],
                email=request.data['email'],
                role=request.data['role'],
                designation=request.data.get('designation'),
            )
            new_user.set_password(request.data['password'])
            new_user.save()
            if branch_id:
                BranchUser.objects.create(branch_id=branch_id, user=new_user)
        return Response(UserSerializer(new_user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_superuser:
            # Scope check: ensure requesting admin has access to this user's branch
            admin_branch_ids = set(_get_admin_branch_ids(request.user))
            user_branch_ids = set(BranchUser.objects.filter(user=user).values_list('branch_id', flat=True))
            if not admin_branch_ids.intersection(user_branch_ids):
                return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response({'message': 'User deleted'})


class ParentListView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def get(self, request):
        user = request.user
        if user.role == 'company_admin':
            branch_ids = user.branches.values_list('id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            parents = User.objects.filter(id__in=user_ids, role='parent')
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            parents = User.objects.filter(id__in=user_ids, role='parent')
        result = []
        for parent in parents:
            children = parent.children.all()
            result.append({
                'id': str(parent.id),
                'name': parent.name,
                'email': parent.email,
                'created_at': parent.created_at,
                'children': [
                    {'id': str(c.id), 'name': c.name, 'branch': c.branch.name}
                    for c in children
                ],
            })
        return Response(result)
