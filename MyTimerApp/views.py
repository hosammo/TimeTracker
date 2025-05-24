from django.shortcuts import render
from django.utils.timezone import now
from timetracker.models import TimeEntry
from projects.models import Project, Task
from datetime import datetime

def home(request):
    today = now().date()
    today_entries = TimeEntry.objects.filter(start_time__date=today, end_time__isnull=False)
    running_entry = TimeEntry.objects.filter(end_time__isnull=True).first()
    recent_entries = TimeEntry.objects.order_by("-start_time")[:5]

    total_minutes = sum([(e.end_time - e.start_time).total_seconds() / 60 for e in today_entries])
    total_hours = round(total_minutes / 60, 2)

    active_projects = Project.objects.filter(archived=False)
    tasks = Task.objects.all()

    return render(request, "home.html", {
        "total_hours": total_hours,
        "running_entry": running_entry,
        "recent_entries": recent_entries,
        "active_projects": active_projects,
        "top_projects": active_projects.order_by("-id")[:3],
        "total_tasks": tasks.count(),
        "active_tasks": tasks.filter(is_active=True).count(),
        "inactive_tasks": tasks.filter(is_active=False).count(),
        "top_tasks": tasks.order_by("-estimated_minutes")[:3],
    })
