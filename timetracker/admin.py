from django.contrib import admin
from .models import TimeEntry

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id", "project", "task", "start_time", "end_time",
        "billable", "hourly_rate", "duration_minutes"
    )
    list_filter = ("billable", "project", "task", "start_time")
    search_fields = ("project__name", "task__name", "description")
    date_hierarchy = "start_time"
