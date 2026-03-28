import uuid
from django.db import models


class AcademicRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('api.Student', on_delete=models.CASCADE, related_name='academic_records')
    class_ref = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='academic_records')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    term = models.CharField(max_length=100)
    subject_name = models.CharField(max_length=255)
    grade_score = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'academic_records'

    def __str__(self):
        return f"{self.student.name} - {self.subject_name} ({self.term})"
