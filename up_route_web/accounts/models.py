from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    api_key = models.CharField(max_length=64, default=None, null=True, blank=True, unique=True)