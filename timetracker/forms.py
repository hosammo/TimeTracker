from django import forms
from .models import TimeEntry

class ManualEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['project', 'task', 'description', 'start_time', 'end_time', 'billable', 'hourly_rate']