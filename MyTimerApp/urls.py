from django.contrib import admin
from django.urls import path, include
from .views import home  # import the new view

urlpatterns = [
    path('', home, name='home'),  # homepage
    path('admin/', admin.site.urls),
    path('tracker/', include('timetracker.urls')),
    path('', include('core.urls')),

]
