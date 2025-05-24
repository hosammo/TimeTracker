# timetracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracker_home, name='tracker_home'),
    path('start/', views.start_timer, name='start_timer'),
    path('stop/<int:entry_id>/', views.stop_timer, name='stop_timer'),
    path('continue/<int:entry_id>/', views.continue_entry, name='continue_entry'),
    path('duplicate/<int:entry_id>/', views.duplicate_entry, name='duplicate_entry'),
    path('edit/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('submit/', views.submit_manual_entry, name='submit_manual_entry'),
    path('tasks/by-project/', views.tasks_by_project, name='tasks_by_project'),
    path('projects/ajax/add/', views.ajax_add_project, name='ajax_add_project'),
    path('tasks/ajax/add/', views.ajax_add_task, name='ajax_add_task'),
]