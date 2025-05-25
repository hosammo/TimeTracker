# timetracker/models.py
from django.db import models
from django.contrib.auth.models import User
from projects.models import Project, Task


class TimeEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def duration_minutes(self):
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return 0

    def __str__(self):
        project_name = self.project.name if self.project else "No Project"
        return f"{project_name} - {self.start_time} to {self.end_time}"

    class Meta:
        ordering = ['-start_time']


class TimeEntryAuditLog(models.Model):
    """Audit log for tracking all changes to time entries"""

    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('RESTORE', 'Restored'),
        ('START_TIMER', 'Started Timer'),
        ('STOP_TIMER', 'Stopped Timer'),
        ('CONTINUE', 'Continued Entry'),
        ('DUPLICATE', 'Duplicated Entry'),
    ]

    time_entry = models.ForeignKey(TimeEntry, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # IP Address and User Agent for security
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Session information
    session_key = models.CharField(max_length=40, blank=True)

    # Previous and current values (JSON field to store changes)
    previous_values = models.JSONField(null=True, blank=True)
    current_values = models.JSONField(null=True, blank=True)

    # Additional context/notes
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_info = f"by {self.user.username}" if self.user else "by anonymous user"
        return f"{self.get_action_display()} TimeEntry #{self.time_entry.id} {user_info} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Time Entry Audit Log"
        verbose_name_plural = "Time Entry Audit Logs"