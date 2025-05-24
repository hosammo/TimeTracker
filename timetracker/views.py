# timetracker/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from timetracker.models import TimeEntry
from projects.models import Project, Task
from core.models import Client, Workspace
from timetracker.forms import ManualEntryForm, StopTimerForm
import pytz
from datetime import datetime


def tracker_home(request):
    running_entry = TimeEntry.objects.filter(end_time__isnull=True).first()
    past_entries = TimeEntry.objects.filter(end_time__isnull=False).order_by('-start_time')
    form = ManualEntryForm()
    projects = Project.objects.filter(archived=False)
    tasks = Task.objects.filter(is_active=True)
    clients = Client.objects.all()

    progress_percent = 0
    if running_entry:
        # Get the first workspace or create a default one
        workspace = Workspace.objects.first()
        if workspace:
            duration = (now() - running_entry.start_time).total_seconds() / 3600
            progress_percent = min(100, int((duration / 8) * 100))

    return render(request, 'timetracker/tracker.html', {
        'running_entry': running_entry,
        'past_entries': past_entries,
        'form': form,
        'projects': projects,
        'tasks': tasks,
        'clients': clients,
        'progress_percent': progress_percent,
        'stop_form': StopTimerForm() if running_entry else None
    })


def start_timer(request):
    if request.method == "POST":
        # Start timer without requiring project/task
        TimeEntry.objects.create(
            description=request.POST.get("description", ""),
            start_time=now()
        )
    return redirect('tracker_home')


def stop_timer(request, entry_id):
    entry = get_object_or_404(TimeEntry, pk=entry_id)

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
            else:
                # Return with error if new project fields are incomplete
                return render(request, 'timetracker/tracker.html', {
                    'error': 'Please provide both project name and client for new project',
                    'running_entry': entry,
                    'stop_form': StopTimerForm(initial={'description': entry.description}),
                    'past_entries': TimeEntry.objects.filter(end_time__isnull=False).order_by('-start_time'),
                    'projects': Project.objects.filter(archived=False),
                    'tasks': Task.objects.filter(is_active=True),
                    'clients': Client.objects.all()
                })

        # Handle new task creation
        if task_id == 'new':
            new_task_name = request.POST.get('new_task_name')

            if new_task_name and project_id and project_id != 'new':
                task = Task.objects.create(
                    name=new_task_name,
                    project_id=project_id
                )
                task_id = task.id
            else:
                task_id = None  # Task is optional, so we can continue without it

        # Validate that we have a project
        if not project_id or project_id == 'new':
            return render(request, 'timetracker/tracker.html', {
                'error': 'Please select or create a project before stopping the timer',
                'running_entry': entry,
                'stop_form': StopTimerForm(initial={'description': entry.description}),
                'past_entries': TimeEntry.objects.filter(end_time__isnull=False).order_by('-start_time'),
                'projects': Project.objects.filter(archived=False),
                'tasks': Task.objects.filter(is_active=True),
                'clients': Client.objects.all()
            })

        # Update the entry
        entry.project_id = project_id
        entry.task_id = task_id if task_id and task_id != 'new' else None
        entry.description = description
        entry.end_time = now()
        entry.save()

        return redirect('tracker_home')
    else:
        # If not POST, just stop the timer with existing data
        if not entry.project:
            # If no project set, redirect back to tracker with error
            return render(request, 'timetracker/tracker.html', {
                'error': 'Please select a project before stopping the timer',
                'running_entry': entry,
                'stop_form': StopTimerForm(initial={'description': entry.description}),
                'past_entries': TimeEntry.objects.filter(end_time__isnull=False).order_by('-start_time'),
                'projects': Project.objects.filter(archived=False),
                'tasks': Task.objects.filter(is_active=True),
                'clients': Client.objects.all()
            })
        entry.end_time = now()
        entry.save()

    return redirect('tracker_home')


def continue_entry(request, entry_id):
    old = get_object_or_404(TimeEntry, pk=entry_id)
    TimeEntry.objects.create(
        project=old.project,
        task=old.task,
        description=old.description,
        start_time=now()
    )
    return redirect('tracker_home')


def duplicate_entry(request, entry_id):
    old = get_object_or_404(TimeEntry, pk=entry_id)
    TimeEntry.objects.create(
        project=old.project,
        task=old.task,
        description=old.description,
        start_time=old.start_time,
        end_time=old.end_time
    )
    return redirect('tracker_home')


def submit_manual_entry(request):
    form = ManualEntryForm(request.POST)
    if form.is_valid():
        form.save()
    return redirect('tracker_home')


def tasks_by_project(request):
    project_id = request.GET.get("project")
    if project_id == 'new':
        # Return empty task list with just the "new" option
        return HttpResponse('''
            <option value="">Select Task (Optional)</option>
            <option value="new">➕ Create New Task</option>
        ''')
    tasks = Task.objects.filter(project_id=project_id, is_active=True) if project_id else []

    # Return HTML with options including the "new" option
    html = '<option value="">Select Task (Optional)</option>'
    for task in tasks:
        html += f'<option value="{task.id}">{task.name}</option>'
    html += '<option value="new">➕ Create New Task</option>'

    return HttpResponse(html)


@csrf_exempt
def ajax_add_project(request):
    name = request.POST.get("name")
    client_id = request.POST.get("client_id")

    if name and client_id:
        Project.objects.create(name=name, client_id=client_id)

    return render(request, "timetracker/partials/project_options.html", {
        "projects": Project.objects.filter(archived=False)
    })


@csrf_exempt
def ajax_add_task(request):
    name = request.POST.get("name")
    project_id = request.POST.get("project_id")

    if name and project_id and project_id.isdigit():
        Task.objects.create(name=name, project_id=int(project_id))

    return render(request, "timetracker/partials/task_options.html", {
        "tasks": Task.objects.filter(project_id=project_id,
                                     is_active=True) if project_id and project_id.isdigit() else []
    })


def edit_entry(request, entry_id):
    entry = get_object_or_404(TimeEntry, pk=entry_id)

    if request.method == "POST":
        # Update entry fields
        entry.project_id = request.POST.get('project')
        entry.task_id = request.POST.get('task') or None
        entry.description = request.POST.get('description', '')

        # Parse datetime inputs
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')

        # Get timezone from first workspace or use UTC
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
        return redirect('tracker_home')

    # For GET request, return the edit form
    projects = Project.objects.filter(archived=False)
    tasks = Task.objects.filter(project=entry.project, is_active=True) if entry.project else []

    return render(request, 'timetracker/partials/edit_entry_form.html', {
        'entry': entry,
        'projects': projects,
        'tasks': tasks,
    })