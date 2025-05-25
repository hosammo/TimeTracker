from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('tracker/', include('timetracker.urls')),
    path('', include('core.urls')),
    path('', include('projects.urls')),  # Add this line
]