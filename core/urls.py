# Enhanced core/urls.py - PRESERVING ALL EXISTING + ADDING NEW

from django.urls import path
from . import views

urlpatterns = [
    # PRESERVE: All existing URLs exactly as they are
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.create_client, name='create_client'),
    path('clients/update/<int:client_id>/', views.update_client, name='update_client'),

    # ADD: New URL for delete functionality (required by enhanced UI)
    path('clients/delete/<int:client_id>/', views.delete_client, name='delete_client'),
]