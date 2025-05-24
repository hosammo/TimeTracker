from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "client", "archived", "color")
    list_filter = ("client", "archived")
    search_fields = ("name", "client__name")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project", "estimated_minutes", "is_active")
    list_filter = ("project", "is_active")
    search_fields = ("name", "project__name")
