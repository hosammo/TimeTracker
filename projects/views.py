# projects/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from django.http import HttpResponse
from core.models import Client


def project_list(request):
    print("project_list POST triggered:", request.POST)
    projects = Project.objects.select_related('client').all().order_by('name')

    # Get unique clients for filtering
    clients = Client.objects.filter(project__isnull=False).distinct().order_by('name')

    # Calculate some statistics
    total_projects = projects.count()
    active_projects = projects.filter(archived=False)
    archived_projects = projects.filter(archived=True)

    context = {
        'projects': projects,
        'clients': clients,
        'total_projects': total_projects,
        'active_projects_count': active_projects.count(),
        'archived_projects_count': archived_projects.count(),
        'unique_clients_count': clients.count(),
    }

    return render(request, 'projects/project_list.html', context)


def task_list(request):
    print("task_list POST triggered:", request.POST)
    tasks = Task.objects.select_related('project', 'project__client').all().order_by('name')

    # Get unique projects for filtering
    projects = Project.objects.filter(task__isnull=False).distinct().order_by('name')

    # Calculate some statistics
    total_tasks = tasks.count()
    active_tasks = tasks.filter(is_active=True)
    inactive_tasks = tasks.filter(is_active=False)

    # Calculate total estimated minutes
    total_estimated_minutes = sum(task.estimated_minutes for task in tasks)

    context = {
        'tasks': tasks,
        'projects': projects,
        'total_tasks': total_tasks,
        'active_tasks_count': active_tasks.count(),
        'inactive_tasks_count': inactive_tasks.count(),
        'unique_projects_count': projects.count(),
        'total_estimated_minutes': total_estimated_minutes,
    }

    return render(request, 'projects/task_list.html', context)


def project_create_modal(request):
    print("project_create_modal POST triggered:", request.POST)
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            projects = Project.objects.select_related('client').all()
            return render(request, 'projects/partials/project_table.html', {'projects': projects})
    else:
        form = ProjectForm()

    # Get clients for the form
    clients = Client.objects.all().order_by('name')

    return render(request, 'projects/partials/project_form.html', {
        'form': form,
        'clients': clients
    })


def task_create_modal(request):
    print("task_create_modal POST triggered:", request.POST)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            tasks = Task.objects.select_related('project', 'project__client').all()
            return render(request, 'projects/partials/task_table.html', {'tasks': tasks})
    else:
        form = TaskForm()

    # Get projects for the form
    projects = Project.objects.select_related('client').filter(archived=False).order_by('name')

    return render(request, 'projects/partials/task_form.html', {
        'form': form,
        'projects': projects
    })


def project_delete(request, pk):
    print("project_delete POST triggered:", request.POST)
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    return redirect('project_list')


def task_delete(request, pk):
    print("task_delete POST triggered:", request.POST)
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('task_list')