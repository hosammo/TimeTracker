from django.contrib import admin
from .models import Workspace, Client

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace", "email", "company")
    list_filter = ("workspace",)
    search_fields = ("name", "email", "company")
