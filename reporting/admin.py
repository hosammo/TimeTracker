from django.contrib import admin
from .models import SavedReport

@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
