from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import random
from datetime import timedelta
from django.utils import timezone


class User(AbstractUser):
    email=models.EmailField(unique=True)
    phone=models.CharField(blank=True,max_length=10)
    is_verified=models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']



class OTP(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    code=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)
    expired_at=models.DateTimeField(null=True,blank=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000,999999))
    
    def save(self,*args,**kwargs):
        if not self.code:
            self.code=self.generate_otp()
        
        if not self.expired_at:
            self.expired_at=timezone.now()+timedelta(minutes=1)
        super().save(*args, **kwargs)
    def is_expired(self):
        return timezone.now()>self.expired_at
    


    
       