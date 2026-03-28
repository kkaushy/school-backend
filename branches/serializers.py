from rest_framework import serializers
from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'location', 'company_admin_id', 'created_at']
