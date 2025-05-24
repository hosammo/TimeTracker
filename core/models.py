from django.db import models
from django.utils.timezone import get_current_timezone_name

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default=get_current_timezone_name)


    def __str__(self):
        return self.name

class Client(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name