from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('SERVICE_PROVIDER', 'Service Provider'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    contact = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=10)
    location = models.CharField(max_length=100,blank=True,null=True)
    category = models.CharField(max_length=50, blank=True, null=True)  # Used only by SERVICE_PROVIDER
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['username', 'contact']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
