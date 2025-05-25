# timetracker/views.py - Enhanced version with modern statistics
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from timetracker.models import TimeEntry, TimeEntryAuditLog
from projects.models import Project, Task
from core.models import Client, Workspace
from timetracker.forms import ManualEntryForm, StopTimerForm
from timetracker.utils import log_time_entry_action, serialize_time_entry
import pytz


def tracker_home(request):
    # Get current time entries
    running_entry = TimeEntry.objects.filter(end_time__isnull=True, deleted=False).first()
    past_entries = TimeEntry.objects.filter(end_time__isnull=False, deleted=False).order_by('-start_time')

    # Calculate statistics
    today = now().date()
    week_start = today - timedelta(days=today.weekday())

    # Today's time
    today_entries = TimeEntry.objects.filter(
        start_time__date=today,
        end_time__isnull=False,
        deleted=False
    )
    today_minutes = sum([(e.end_time - e.start_time).total_seconds() / 60 for e in today_entries])
    today_hours = today_minutes / 60

    # This week's time
    week_entries = TimeEntry.objects.filter(
        start_time__date__gte=week_start,
        end_time__isnull=False,
        deleted=False
    )
    week_minutes = sum([(e.end_time - e.start_time).total_seconds() / 60 for e in week_entries])
    week_hours = week_minutes / 60

    # Active projects count
    active_projects = Project.objects.filter(archived=False)
    active_projects_count = active_projects.count()

    # Form and data for templates
    form = ManualEntryForm()
    projects = Project.objects.filter(archived=False).order_by('name')
    tasks = Task.objects.filter(is_active=True).order_by('name')
    clients = Client.objects.all().order_by('name')

    # Progress calculation for running timer
    progress_percent = 0
    if running_entry:
        workspace = Workspace.objects.first()
        if workspace:
            duration = (now() - running_entry.start_time).total_seconds() / 3600
            progress_percent = min(100, int((duration / 8) * 100))  # 8 hours = 100%

    context = {
        'running_entry': running_entry,
        'past_entries': past_entries[:20],  # Limit to recent 20 entries
        'form': form,
        'projects': projects,
        'tasks': tasks,
        'clients': clients,
        'progress_percent': progress_percent,
        'stop_form': StopTimerForm() if running_entry else None,

        # Enhanced statistics
        'today_hours': today_hours,
        'week_hours': week_hours,
        'active_projects_count': active_projects_count,
        'total_entries_count': past_entries.count(),

        # Additional context for better UX
        'today_entries_count': today_entries.count(),
        'week_entries_count': week_entries.count(),
    }

    return render(request, 'timetracker/tracker.html', context)


def discard_timer(request, entry_id):
    """Discard a running timer without saving it"""
    entry = get_object_or_404(TimeEntry, pk=entry_id, end_time__isnull=True, deleted=False)

    if request.method == "POST":
        # Store entry info for logging before deletion
        description = entry.description or "No description"
        duration_seconds = (now() - entry.start_time).total_seconds()
        duration_minutes = int(duration_seconds / 60)

        # Log the discard action
        log_time_entry_action(
            request,
            entry,
            'DELETE',  # Using DELETE action type for discarded timers
            notes=f"Timer discarded without saving. Duration: {duration_minutes} minutes, Description: '{description}'"
        )

        # Permanently delete the entry (not soft delete since it was never "completed")
        entry.delete()

        messages.info(request, f"Timer discarded. No time was saved from your {duration_minutes}-minute session.")
        return redirect('tracker_home')

    return redirect('tracker_home')


def start_timer(request):
    if request.method == "POST":
        # Check if there's already a running timer
        existing_timer = TimeEntry.objects.filter(end_time__isnull=True, deleted=False).first()
        if existing_timer:
            messages.warning(request, "You already have a timer running. Please stop it first.")
            return redirect('tracker_home')

        time_entry = TimeEntry.objects.create(
            description=request.POST.get("description", ""),
            start_time=now()
        )

        # Log the action
        log_time_entry_action(
            request,
            time_entry,
            'START_TIMER',
            notes=f"Timer started with description: '{time_entry.description}'"
        )

        messages.success(request, "Timer started successfully! Configure project details when you're ready to stop.")

    return redirect('tracker_home')


def stop_timer(request, entry_id):
    entry = get_object_or_404(TimeEntry, pk=entry_id, deleted=False)

    # Store previous state for logging
    previous_values = serialize_time_entry(entry)

    if request.method == "POST":
        project_id = request.POST.get('project')
        task_id = request.POST.get('task')
        description = request.POST.get('description', '')

        # Handle new project creation
        if project_id == 'new':
            new_project_name = request.POST.get('new_project_name')
            new_project_client = request.POST.get('new_project_client')

            if new_project_name and new_project_client:
                project = Project.objects.create(
                    name=new_project_name,
                    client_id=new_project_client
                )
                project_id = project.id
                messages.success(request, f"New project '{new_project_name}' created successfully!")
            else:
                messages.error(request, "Please provide both project name and client for new project.")
                return redirect('tracker_home')

        # Handle new task creation
        if task_id == 'new':
            new_task_name = request.POST.get('new_task_name')

            if new_task_name and project_id and project_id != 'new':
                task = Task.objects.create(
                    name=new_task_name,
                    project_id=project_id
                )
                task_id = task.id
                messages.success(request, f"New task '{new_task_name}' created successfully!")
            else:
                task_id = None

        # Validate project selection
        if not project_id or project_id == 'new':
            messages.error(request, "Please select or create a project before stopping the timer.")
            return redirect('tracker_home')

        # Update the entry
        entry.project_id = project_id
        entry.task_id = task_id if task_id and task_id != 'new' else None
        entry.description = description
        entry.end_time = now()
        entry.save()

        # Calculate duration for success message
        duration_minutes = entry.duration_minutes()
        duration_text = f"{duration_minutes // 60}h {duration_minutes % 60}m" if duration_minutes >= 60 else f"{duration_minutes}m"

        # Log the action
        log_time_entry_action(
            request,
            entry,
            'STOP_TIMER',
            previous_values=previous_values,
            notes=f"Timer stopped. Duration: {duration_minutes} minutes"
        )

        messages.success(request, f"Timer stopped! You tracked {duration_text} on {entry.project.name}.")
        return redirect('tracker_home')

    # Handle GET request (shouldn't happen in normal flow)
    entry.end_time = now()
    entry.save()

    log_time_entry_action(
        request,
        entry,
        'STOP_TIMER',
        previous_values=previous_values,
        notes=f"Timer stopped without changes. Duration: {entry.duration_minutes()} minutes"
    )

    return redirect('tracker_home')


def continue_entry(request, entry_id):
    old = get_object_or_404(TimeEntry, pk=entry_id, deleted=False)

    # Check if there's already a running timer
    existing_timer = TimeEntry.objects.filter(end_time__isnull=True, deleted=False).first()
    if existing_timer:
        messages.warning(request, "Please stop your current timer before starting a new one.")
        return redirect('tracker_home')

    new_entry = TimeEntry.objects.create(
        project=old.project,
        task=old.task,
        description=old.description,
        start_time=now()
    )

    # Log both the original entry reference and new entry creation
    log_time_entry_action(
        request,
        new_entry,
        'CONTINUE',
        notes=f"Continued from TimeEntry #{old.id} ({old.project.name if old.project else 'No project'})"
    )

    messages.success(request, f"Timer started for {old.project.name if old.project else 'your task'}!")
    return redirect('tracker_home')


def duplicate_entry(request, entry_id):
    old = get_object_or_404(TimeEntry, pk=entry_id, deleted=False)
    new_entry = TimeEntry.objects.create(
        project=old.project,
        task=old.task,
        description=old.description,
        start_time=old.start_time,
        end_time=old.end_time,
        billable=old.billable,
        hourly_rate=old.hourly_rate
    )

    # Log the duplication
    log_time_entry_action(
        request,
        new_entry,
        'DUPLICATE',
        notes=f"Duplicated from TimeEntry #{old.id}. Duration: {new_entry.duration_minutes()} minutes"
    )

    messages.success(request, f"Time entry duplicated successfully!")
    return redirect('tracker_home')


def delete_entry(request, entry_id):
    """Soft delete a time entry with comprehensive logging"""
    entry = get_object_or_404(TimeEntry, pk=entry_id, deleted=False)

    if request.method == "POST":
        # Store previous state for logging
        previous_values = serialize_time_entry(entry)

        # Perform soft delete
        entry.deleted = True
        entry.deleted_at = now()
        entry.save()

        # Log the deletion with detailed information
        log_time_entry_action(
            request,
            entry,
            'DELETE',
            previous_values=previous_values,
            notes=f"Soft deleted entry. Project: {entry.project.name if entry.project else 'No project'}, Duration: {entry.duration_minutes()} minutes"
        )

        messages.success(request, f"Time entry deleted successfully. You can restore it from the deleted entries page.")
        return redirect('tracker_home')

    return redirect('tracker_home')


def restore_entry(request, entry_id):
    """Restore a soft-deleted time entry with comprehensive logging"""
    entry = get_object_or_404(TimeEntry, pk=entry_id, deleted=True)

    if request.method == "POST":
        # Store previous state for logging
        previous_values = serialize_time_entry(entry)

        # Perform restore
        entry.deleted = False
        entry.deleted_at = None
        entry.save()

        # Log the restoration with detailed information
        log_time_entry_action(
            request,
            entry,
            'RESTORE',
            previous_values=previous_values,
            notes=f"Restored deleted entry. Project: {entry.project.name if entry.project else 'No project'}, Duration: {entry.duration_minutes()} minutes"
        )

        messages.success(request, f"Time entry restored successfully.")
        return redirect('deleted_entries')

    return redirect('deleted_entries')


def deleted_entries(request):
    """Show all deleted entries with restore option"""
    deleted_entries = TimeEntry.objects.filter(deleted=True).order_by('-deleted_at')

    return render(request, 'timetracker/deleted_entries.html', {
        'deleted_entries': deleted_entries,
    })


def audit_logs(request):
    """Show audit logs for time entries"""
    logs = TimeEntryAuditLog.objects.select_related('user', 'time_entry').order_by('-timestamp')

    # Filter by action if specified
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)

    # Filter by user if specified
    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user_id=user_filter)

    # Filter by date range if specified
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)  # Show 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get unique users and actions for filters
    from django.contrib.auth.models import User
    users = User.objects.filter(timeentryauditlog__isnull=False).distinct()
    actions = TimeEntryAuditLog.ACTION_CHOICES

    return render(request, 'timetracker/audit_logs.html', {
        'page_obj': page_obj,
        'users': users,
        'actions': actions,
        'current_filters': {
            'action': action_filter,
            'user': user_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    })


def submit_manual_entry(request):
    if request.method == "POST":
        form = ManualEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()

            # Log manual entry creation
            log_time_entry_action(
                request,
                entry,
                'CREATE',
                notes=f"Manual entry created. Duration: {entry.duration_minutes()} minutes"
            )

            duration_minutes = entry.duration_minutes()
            duration_text = f"{duration_minutes // 60}h {duration_minutes % 60}m" if duration_minutes >= 60 else f"{duration_minutes}m"
            messages.success(request,
                             f"Manual entry saved! {duration_text} tracked for {entry.project.name if entry.project else 'your task'}.")
        else:
            messages.error(request, "Please correct the errors in the form.")

    return redirect('tracker_home')


def edit_entry(request, entry_id):
    entry = get_object_or_404(TimeEntry, pk=entry_id, deleted=False)

    if request.method == "POST":
        # Store previous state for logging
        previous_values = serialize_time_entry(entry)

        # Update entry
        entry.project_id = request.POST.get('project')
        entry.task_id = request.POST.get('task') or None
        entry.description = request.POST.get('description', '')

        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')

        workspace = Workspace.objects.first()
        tz = pytz.timezone(workspace.timezone) if workspace and hasattr(workspace, 'timezone') else pytz.UTC

        if start_date and start_time:
            naive_start = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            entry.start_time = tz.localize(naive_start)

        if end_date and end_time:
            naive_end = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
            entry.end_time = tz.localize(naive_end)

        entry.billable = request.POST.get('billable') == 'on'
        hourly_rate = request.POST.get('hourly_rate', '0')
        entry.hourly_rate = float(hourly_rate) if hourly_rate else 0

        entry.save()

        # Log the update
        log_time_entry_action(
            request,
            entry,
            'UPDATE',
            previous_values=previous_values,
            notes=f"Entry updated. New duration: {entry.duration_minutes()} minutes"
        )

        messages.success(request, "Time entry updated successfully!")
        return redirect('tracker_home')

    # For GET request, return the edit form
    projects = Project.objects.filter(archived=False).order_by('name')
    tasks = Task.objects.filter(project=entry.project, is_active=True).order_by('name') if entry.project else []

    return render(request, 'timetracker/partials/edit_entry_form.html', {
        'entry': entry,
        'projects': projects,
        'tasks': tasks,
    })


# Keep existing utility functions unchanged
def tasks_by_project(request):
    project_id = request.GET.get("project")

    if project_id == 'new':
        # Return empty task list for new projects
        return render(request, 'timetracker/partials/task_dropdown.html', {'tasks': []})

    tasks = Task.objects.filter(project_id=project_id, is_active=True).order_by('name') if project_id else []

    return render(request, 'timetracker/partials/task_dropdown.html', {'tasks': tasks})


def tasks_by_project_edit(request):
    """Separate endpoint for edit form task loading"""
    project_id = request.GET.get("project")
    selected_task_id = request.GET.get("selected_task_id")

    tasks = Task.objects.filter(project_id=project_id, is_active=True).order_by('name') if project_id else []

    return render(request, 'timetracker/partials/edit_task_dropdown.html', {
        'tasks': tasks,
        'selected_task_id': int(selected_task_id) if selected_task_id else None
    })


@csrf_exempt
def ajax_add_project(request):
    name = request.POST.get("name")
    client_id = request.POST.get("client_id")

    if name and client_id:
        Project.objects.create(name=name, client_id=client_id)

    return render(request, "timetracker/partials/project_options.html", {
        "projects": Project.objects.filter(archived=False).order_by('name')
    })


@csrf_exempt
def ajax_add_task(request):
    name = request.POST.get("name")
    project_id = request.POST.get("project_id")

    if name and project_id and project_id.isdigit():
        Task.objects.create(name=name, project_id=int(project_id))

    return render(request, "timetracker/partials/task_options.html", {
        "tasks": Task.objects.filter(project_id=project_id,
                                     is_active=True).order_by('name') if project_id and project_id.isdigit() else []
    })