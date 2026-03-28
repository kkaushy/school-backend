import uuid
from django.db import models


class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classes'

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


class ClassStudent(models.Model):
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_students')
    student = models.ForeignKey('api.Student', on_delete=models.CASCADE, related_name='class_enrollments')

    class Meta:
        db_table = 'class_students'
        unique_together = ('class_ref', 'student')


class ClassTeacher(models.Model):
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_teachers')
    teacher = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='teaching_classes')

    class Meta:
        db_table = 'class_teachers'
        unique_together = ('class_ref', 'teacher')
