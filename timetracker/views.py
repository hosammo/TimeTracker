from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from timetracker.models import TimeEntry
from projects.models import Project, Task
from core.models import Client, Workspace  # Make sure this is your correct import
from timetracker.forms import ManualEntryForm
from django.utils.timezone import now
import pytz

def tracker_home(request):
    running_entry = TimeEntry.objects.filter(end_time__isnull=True).first()
    past_entries = TimeEntry.objects.filter(end_time__isnull=False).order_by('-start_time')
    form = ManualEntryForm()
    projects = Project.objects.all()
    tasks = Task.objects.all()
    clients = Client.objects.all()

    progress_percent = 0
    if running_entry:
        duration = (get_workspace_now(Workspace) - running_entry.start_time).total_seconds() / 3600
        progress_percent = min(100, int((duration / 8) * 100))

    return render(request, 'timetracker/tracker.html', {
        'running_entry': running_entry,
        'past_entries': past_entries,
        'form': form,
        'projects': projects,
        'tasks': tasks,
        'clients': clients,
        'progress_percent': progress_percent
    })

def start_timer(request):
    if request.method == "POST":
        TimeEntry.objects.create(
            project_id=request.POST.get("project"),
            task_id=request.POST.get("task") or None,
            description=request.POST.get("description"),
            start_time=get_workspace_now(Workspace)
        )
    return redirect('tracker_home')

def stop_timer(request, entry_id):
    entry = get_object_or_404(TimeEntry, pk=entry_id)
    entry.end_time = get_workspace_now(Workspace)
    entry.save()
    return redirect('tracker_home')

def continue_entry(request, entry_id):
    old = get_object_or_404(TimeEntry, pk=entry_id)
    TimeEntry.objects.create(
        project=old.project,
        task=old.task,
        description=old.description,
        start_time=get_workspace_now(Workspace)
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
    tasks = Task.objects.filter(project_id=project_id)
    return render(request, "timetracker/partials/task_options.html", {"tasks": tasks})

@csrf_exempt
def ajax_add_project(request):
    from core.models import Client
    name = request.POST.get("name")
    client_id = request.POST.get("client_id")
    new_client_name = request.POST.get("new_client_name")

    if new_client_name:
        client = Client.objects.create(name=new_client_name)
        client_id = client.id

    if name and client_id:
        Project.objects.create(name=name, client_id=client_id)

    # Always return this to refresh the project dropdown
    return render(request, "timetracker/partials/project_options.html", {
        "projects": Project.objects.all()
    })



@csrf_exempt
def ajax_add_task(request):
    name = request.POST.get("name")
    project_id = request.POST.get("project_id")

    if name and project_id and project_id.isdigit():
        Task.objects.create(name=name, project_id=int(project_id))

    return render(request, "timetracker/partials/task_options.html", {
        "tasks": Task.objects.filter(project_id=project_id) if project_id and project_id.isdigit() else []
    })

def get_workspace_now(workspace):
    if not hasattr(workspace, "timezone") or not isinstance(workspace.timezone, str):
        raise ValueError("Expected workspace instance with a valid timezone string.")

    return now().astimezone(pytz.timezone(workspace.timezone))
