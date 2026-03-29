from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Branch, BranchUser
from .serializers import BranchSerializer
from api.permissions import require_roles
from api.constants import COMPANY_ADMIN


class BranchListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser:
            branches = Branch.objects.all()
        elif user.role == COMPANY_ADMIN:
            branches = Branch.objects.filter(company_admin=user)
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
            branches = Branch.objects.filter(id__in=branch_ids)
        return Response(BranchSerializer(branches, many=True).data)

    @require_roles('company_admin')
    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'message': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)
        branch = Branch.objects.create(
            name=name,
            location=request.data.get('location'),
            company_admin=request.user,
        )
        return Response(BranchSerializer(branch).data, status=status.HTTP_201_CREATED)


class BranchDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_branch(self, pk, user):
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return None, Response({'message': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_superuser and user.role == COMPANY_ADMIN and branch.company_admin != user:
            return None, Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        return branch, None

    @require_roles(COMPANY_ADMIN)
    def put(self, request, pk):
        branch, err = self._get_branch(pk, request.user)
        if err:
            return err
        if 'name' in request.data:
            branch.name = request.data['name']
        if 'location' in request.data:
            branch.location = request.data['location']
        branch.save()
        return Response(BranchSerializer(branch).data)

    @require_roles(COMPANY_ADMIN)
    def delete(self, request, pk):
        branch, err = self._get_branch(pk, request.user)
        if err:
            return err
        branch.delete()
        return Response({'message': 'Branch deleted successfully'})
