# Enhanced projects/views.py - PRESERVING ALL EXISTING FUNCTIONALITY

from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from django.http import HttpResponse


def project_list(request):
    # PRESERVE: All existing functionality
    print("project_list POST triggered:", request.POST)
    projects = Project.objects.all()

    # ADD: Statistics for new template (without changing existing logic)
    active_projects_count = projects.filter(archived=False).count()
    archived_projects_count = projects.filter(archived=True).count()
    unique_clients_count = projects.values('client').distinct().count()

    # PRESERVE: Original render call, just ADD new context
    return render(request, 'projects/project_list.html', {
        'projects': projects,  # Keep existing
        # ADD: New context for template statistics
        'active_projects_count': active_projects_count,
        'archived_projects_count': archived_projects_count,
        'unique_clients_count': unique_clients_count,
    })


def task_list(request):
    # PRESERVE: All existing functionality
    print("task_list POST triggered:", request.POST)
    tasks = Task.objects.select_related('project').all()

    # ADD: Context for new template features (without changing existing logic)
    total_estimated_minutes = sum(task.estimated_minutes for task in tasks if task.estimated_minutes)
    total_estimated_hours = round(total_estimated_minutes / 60, 1) if total_estimated_minutes > 0 else 0
    unique_projects = Project.objects.filter(task__in=tasks).distinct() if tasks else []

    # PRESERVE: Original render call, just ADD new context
    return render(request, 'projects/task_list.html', {
        'tasks': tasks,  # Keep existing
        # ADD: New context for template enhancements
        'total_estimated_time': total_estimated_hours,
        'unique_projects': unique_projects,
    })


def project_create_modal(request):
    # PRESERVE: All existing functionality exactly as is
    print("project_create_modal POST triggered:", request.POST)
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            projects = Project.objects.all()
            return render(request, 'projects/partials/project_table.html', {'projects': projects})
    else:
        form = ProjectForm()
    return render(request, 'projects/partials/project_form.html', {'form': form})


def task_create_modal(request):
    # PRESERVE: All existing functionality exactly as is
    print("task_create_modal POST triggered:", request.POST)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            tasks = Task.objects.select_related('project').all()
            return render(request, 'projects/partials/task_table.html', {'tasks': tasks})
    else:
        form = TaskForm()
    return render(request, 'projects/partials/task_form.html', {'form': form})


# PRESERVE: All existing functions exactly as they are
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm


def project_delete(request, pk):
    # PRESERVE: Exactly as is
    print("project_delete POST triggered:", request.POST)
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    return redirect('project_list')


def task_delete(request, pk):
    # PRESERVE: Exactly as is
    print("task_delete POST triggered:", request.POST)
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('task_list')