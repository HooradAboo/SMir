from django.contrib.auth.models import User
from django.db import models


class UserCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    credentials = models.CharField(max_length=100, blank=True, null=True)
