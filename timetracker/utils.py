# timetracker/utils.py
from django.contrib.auth.models import User
from .models import TimeEntryAuditLog
import json


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


def serialize_time_entry(time_entry):
    """Serialize time entry data for logging"""
    return {
        'id': time_entry.id,
        'project_id': time_entry.project.id if time_entry.project else None,
        'project_name': time_entry.project.name if time_entry.project else None,
        'task_id': time_entry.task.id if time_entry.task else None,
        'task_name': time_entry.task.name if time_entry.task else None,
        'description': time_entry.description,
        'start_time': time_entry.start_time.isoformat() if time_entry.start_time else None,
        'end_time': time_entry.end_time.isoformat() if time_entry.end_time else None,
        'billable': time_entry.billable,
        'hourly_rate': str(time_entry.hourly_rate),
        'deleted': time_entry.deleted,
        'deleted_at': time_entry.deleted_at.isoformat() if time_entry.deleted_at else None,
        'duration_minutes': time_entry.duration_minutes(),
    }


def log_time_entry_action(request, time_entry, action, previous_values=None, notes=''):
    """
    Log an action performed on a time entry

    Args:
        request: Django request object
        time_entry: TimeEntry instance
        action: Action type (CREATE, UPDATE, DELETE, RESTORE, etc.)
        previous_values: Previous state of the time entry (for updates)
        notes: Additional notes about the action
    """
    # Get user (handle anonymous users)
    user = request.user if request.user.is_authenticated else None

    # Get current state
    current_values = serialize_time_entry(time_entry)

    # Create audit log entry
    audit_log = TimeEntryAuditLog.objects.create(
        time_entry=time_entry,
        action=action,
        user=user,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        session_key=request.session.session_key or '',
        previous_values=previous_values,
        current_values=current_values,
        notes=notes
    )

    return audit_log


def log_bulk_action(request, time_entries, action, notes=''):
    """Log actions that affect multiple time entries"""
    logs = []
    for entry in time_entries:
        log = log_time_entry_action(request, entry, action, notes=notes)
        logs.append(log)
    return logs