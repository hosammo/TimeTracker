from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from django.http import HttpResponse


def project_list(request):
    print("project_list POST triggered:", request.POST)
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})


def task_list(request):
    print("task_list POST triggered:", request.POST)
    tasks = Task.objects.select_related('project').all()
    return render(request, 'projects/task_list.html', {'tasks': tasks})


def project_create_modal(request):
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


from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
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