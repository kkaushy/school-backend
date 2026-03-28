import uuid
from django.db import models

FREQUENCY_CHOICES = [
    ('monthly', 'Monthly'), ('quarterly', 'Quarterly'),
    ('yearly', 'Yearly'), ('one-time', 'One-Time'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue'),
]


class FeeHead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='fee_heads')
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_heads'
        ordering = ['name']

    def __str__(self):
        return self.name


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('api.Student', on_delete=models.CASCADE, related_name='payments')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    fee_head = models.ForeignKey(FeeHead, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.student.name} - {self.amount} ({self.status})"
