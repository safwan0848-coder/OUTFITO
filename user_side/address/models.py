from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Address(models.Model):

    TYPE_CHOICES = [
        ("home", "Home"),
        ("work", "Work"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")

    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True,null=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    type = models.CharField(max_length=10,choices=TYPE_CHOICES,default="home")
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name