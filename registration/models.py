from django.db import models
from service.models import Service

class User(models.Model):
    USER_TYPE_CHOICES = (
        ('USER', 'User'),
        ('SERVICE_PROVIDER', 'Service Provider'),
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=10)
    location = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='SERVICE_PROVIDER_CATEGORY')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255, unique=True)           # Refresh token
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.email} (Expires: {self.expired_at})"
