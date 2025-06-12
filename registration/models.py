from django.contrib.auth.models import AbstractUser
from django.db import models
from service.models import Service

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('USER', 'User'),
        ('SERVICE_PROVIDER', 'Service Provider'),
    )

    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=10)
    location = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='SERVICE_PROVIDER_CATEGORY')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # Remove group-related fields
    groups = None
    user_permissions = None

    def __str__(self):
        return self.email


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255, unique=True)           # Refresh token
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.email} (Expires: {self.expired_at})"
