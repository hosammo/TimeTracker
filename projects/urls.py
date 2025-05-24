from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.project_list, name='project_list'),
    path('projects/delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/delete/<int:pk>/', views.task_delete, name='task_delete'),
    path('projects/new/', views.project_create_modal, name='project_create_modal'),
    path('tasks/new/', views.task_create_modal, name='task_create_modal'),
]
