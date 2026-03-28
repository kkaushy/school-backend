import uuid
from django.db import models


class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    company_admin = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='branches')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'branches'

    def __str__(self):
        return self.name


class BranchUser(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_users')
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='branch_memberships')

    class Meta:
        db_table = 'branch_users'
        unique_together = ('branch', 'user')
