import uuid
from django.db import models

DAY_CHOICES = [
    ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday'),
]


class TimetableSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_ref = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='timetable_slots')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=255)
    teacher = models.ForeignKey('api.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_slots')
    room = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'timetable_slots'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.class_ref.name} - {self.day_of_week} {self.start_time}"
