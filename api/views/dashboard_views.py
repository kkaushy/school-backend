from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Student
from ..permissions import require_roles
from branches.models import Branch, BranchUser
from fees.models import Payment


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def get(self, request):
        user = request.user
        if user.is_superuser:
            branch_ids = Branch.objects.values_list('id', flat=True)
        elif user.role == 'company_admin':
            branch_ids = user.branches.values_list('id', flat=True)
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)

        students = Student.objects.filter(branch_id__in=branch_ids).count()
        branches = Branch.objects.filter(id__in=branch_ids).count()
        from api.models import User as UserModel
        staff = UserModel.objects.filter(
            id__in=BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True),
            role__in=['teacher', 'branch_admin'],
        ).count()
        from django.db.models import Sum
        revenue = Payment.objects.filter(
            branch_id__in=branch_ids, status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({'students': students, 'branches': branches, 'staff': staff, 'revenue': float(revenue)})
