# Enhanced projects/forms.py - Professional form styling

from django import forms
from .models import Project, Task
from core.models import Client


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['client', 'name', 'color', 'archived']
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name',
                'required': True
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control form-control-color',
                'type': 'color',
                'style': 'width: 60px; height: 38px;'
            }),
            'archived': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default color if not provided
        if not self.instance.pk:
            self.fields['color'].initial = '#03a9f4'

        # Populate client choices
        self.fields['client'].queryset = Client.objects.select_related('workspace').all()

        # Add autofocus to name field
        self.fields['name'].widget.attrs.update({'autofocus': True})


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'name', 'estimated_minutes', 'is_active']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task name',
                'required': True
            }),
            'estimated_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '15',
                'placeholder': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate project choices with active projects
        self.fields['project'].queryset = Project.objects.filter(archived=False).select_related('client')

        # Set default values
        if not self.instance.pk:
            self.fields['is_active'].initial = True
            self.fields['estimated_minutes'].initial = 0

        # Add autofocus to name field
        self.fields['name'].widget.attrs.update({'autofocus': True})

        # Add help text
        self.fields['estimated_minutes'].help_text = 'Estimated time in minutes (optional)'
        self.fields['is_active'].help_text = 'Active tasks appear in time tracking'