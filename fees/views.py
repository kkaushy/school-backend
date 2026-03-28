import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import FeeHead, Payment
from .serializers import FeeHeadSerializer, PaymentSerializer
from api.permissions import require_roles
from branches.models import BranchUser


def get_admin_branch_ids(user):
    if user.role == 'company_admin':
        return list(user.branches.values_list('id', flat=True))
    return list(BranchUser.objects.filter(user=user).values_list('branch_id', flat=True))


class FeeHeadListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def get(self, request):
        branch_ids = get_admin_branch_ids(request.user)
        fee_heads = FeeHead.objects.filter(branch_id__in=branch_ids, is_active=True)
        return Response(FeeHeadSerializer(fee_heads, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['branch_id', 'name', 'amount', 'frequency']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        fee_head = FeeHead.objects.create(
            branch_id=request.data['branch_id'],
            name=request.data['name'],
            amount=request.data['amount'],
            frequency=request.data['frequency'],
            description=request.data.get('description'),
        )
        return Response(FeeHeadSerializer(fee_head).data, status=status.HTTP_201_CREATED)


class FeeHeadDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            fee_head = FeeHead.objects.get(pk=pk)
        except FeeHead.DoesNotExist:
            return Response({'message': 'Fee head not found'}, status=status.HTTP_404_NOT_FOUND)
        fee_head.is_active = False
        fee_head.save()
        return Response({'message': 'Fee head deactivated'})


class GenerateInvoicesView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        fee_head_id = request.data.get('fee_head_id')
        due_date = request.data.get('due_date')
        student_ids = request.data.get('student_ids', [])
        if not fee_head_id or not due_date:
            return Response({'message': 'fee_head_id and due_date are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fee_head = FeeHead.objects.get(pk=fee_head_id)
        except FeeHead.DoesNotExist:
            return Response({'message': 'Fee head not found'}, status=status.HTTP_404_NOT_FOUND)
        from api.models import Student
        if student_ids:
            students = Student.objects.filter(id__in=student_ids, branch=fee_head.branch)
        else:
            students = Student.objects.filter(branch=fee_head.branch)
        with transaction.atomic():
            payments = [
                Payment(
                    student=student,
                    branch=fee_head.branch,
                    fee_head=fee_head,
                    amount=fee_head.amount,
                    description=fee_head.name,
                    due_date=due_date,
                )
                for student in students
            ]
            Payment.objects.bulk_create(payments)
        return Response({'message': f'Generated {len(payments)} invoices', 'count': len(payments)}, status=status.HTTP_201_CREATED)


class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ('company_admin', 'branch_admin'):
            branch_ids = get_admin_branch_ids(user)
            payments = Payment.objects.filter(branch_id__in=branch_ids)
        elif user.role == 'parent':
            student_ids = user.children.values_list('id', flat=True)
            payments = Payment.objects.filter(student_id__in=student_ids)
        elif user.role == 'student':
            try:
                payments = Payment.objects.filter(student=user.student_profile)
            except Exception:
                payments = Payment.objects.none()
        else:
            return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        return Response(PaymentSerializer(payments, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['student_id', 'branch_id', 'amount', 'due_date']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        payment = Payment.objects.create(
            student_id=request.data['student_id'],
            branch_id=request.data['branch_id'],
            amount=request.data['amount'],
            description=request.data.get('description'),
            due_date=request.data['due_date'],
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentPayView(APIView):
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def put(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'message': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        payment.status = 'paid'
        payment.paid_date = datetime.date.today()
        payment.save()
        return Response(PaymentSerializer(payment).data)
