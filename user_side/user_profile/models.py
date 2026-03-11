from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import random
from datetime import timedelta
from django.utils import timezone


class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)

    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)

    google_image = models.URLField(blank=True, null=True)   # IMPORTANT
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
