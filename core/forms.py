# NEW: core/forms.py - Professional form handling

from django import forms
from .models import Client, Workspace


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['workspace', 'name', 'email', 'company']
        widgets = {
            'workspace': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'client@example.com'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': True})
        self.fields['email'].required = False
        self.fields['company'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError('Please enter a valid email address.')
        return email


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ['name', 'timezone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Workspace name',
                'required': True
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-select'
            }),
        }