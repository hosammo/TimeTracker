from django.db import models
from projects.models import Project, Task

class TimeEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def duration_minutes(self):
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def __str__(self):
        return f"{self.project.name} - {self.start_time} to {self.end_time}"