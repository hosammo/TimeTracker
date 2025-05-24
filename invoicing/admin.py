from django.contrib import admin
from .models import Invoice, InvoiceItem
from import_export.admin import ExportMixin


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

def mark_as_paid(modeladmin, request, queryset):
    queryset.update(paid=True)

@admin.register(Invoice)
class InvoiceAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "client", "issue_date", "due_date", "paid", "total_amount")
    list_filter = ("client", "paid")
    search_fields = ("client__name",)
    inlines = [InvoiceItemInline]
    date_hierarchy = "issue_date"
    actions = [mark_as_paid]

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "description", "hours", "rate", "amount")
    list_filter = ("invoice",)
    search_fields = ("description", "invoice__client__name")
