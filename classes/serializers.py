from rest_framework import serializers
from .models import Class


class ClassSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'branch_id', 'branch_name', 'created_at']
