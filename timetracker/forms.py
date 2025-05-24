# timetracker/forms.py
from django import forms
from .models import TimeEntry
from projects.models import Project, Task

class ManualEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['project', 'task', 'description', 'start_time', 'end_time', 'billable', 'hourly_rate']

class StopTimerForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(archived=False),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    task = forms.ModelChoiceField(
        queryset=Task.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What did you work on?'})
    )