from rest_framework import serializers
from .models import FeeHead, Payment


class FeeHeadSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = FeeHead
        fields = ['id', 'branch_id', 'branch_name', 'name', 'amount', 'frequency', 'description', 'is_active', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'student_id', 'student_name', 'branch_id', 'branch_name',
                  'fee_head_id', 'amount', 'description', 'status', 'due_date', 'paid_date', 'created_at']
