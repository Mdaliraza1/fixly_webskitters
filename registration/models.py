from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from service.models import Service
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

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

    def clean(self):
        if self.user_type == 'SERVICE_PROVIDER' and not self.category:
            raise ValidationError({'category': 'Category is required for service providers'})
        if self.user_type == 'USER' and self.category:
            raise ValidationError({'category': 'Regular users should not have a category'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.email} (Expires: {self.expired_at})"

    class Meta:
        verbose_name = 'User Token'
        verbose_name_plural = 'User Tokens'
        ordering = ['-created_at']

class Dashboard(models.Model):
    """
    A dummy model for the admin dashboard.
    This model is not meant to be used for storing data.
    """
    class Meta:
        managed = False
        verbose_name_plural = 'Dashboard'
        app_label = 'registration'

    def __str__(self):
        return 'Dashboard'
