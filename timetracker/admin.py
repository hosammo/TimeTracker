# timetracker/admin.py
from django.contrib import admin
from .models import TimeEntry, TimeEntryAuditLog


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id", "project", "task", "start_time", "end_time",
        "billable", "hourly_rate", "duration_minutes", "deleted"
    )
    list_filter = ("billable", "deleted", "project", "task", "start_time")
    search_fields = ("project__name", "task__name", "description")
    date_hierarchy = "start_time"
    readonly_fields = ("deleted_at",)


@admin.register(TimeEntryAuditLog)
class TimeEntryAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id", "time_entry", "action", "user", "timestamp", "ip_address"
    )
    list_filter = ("action", "timestamp", "user")
    search_fields = ("time_entry__id", "user__username", "notes", "ip_address")
    date_hierarchy = "timestamp"
    readonly_fields = (
        "time_entry", "action", "user", "timestamp", "ip_address",
        "user_agent", "session_key", "previous_values", "current_values",
        "notes", "created_at"
    )

    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs for integrity
        return False