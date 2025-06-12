from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.core.exceptions import ValidationError
from service.models import Service
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Explicitly remove groups and user_permissions fields.
    """
    # Remove the groups and user_permissions fields
    groups = None
    user_permissions = None

    USER_TYPE_CHOICES = (
        ('USER', 'User'),
        ('SERVICE_PROVIDER', 'Service Provider'),
    )

    # Override email field to make it unique
    email = models.EmailField(_('email address'), unique=True)
    
    # Custom fields
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='USER',
        verbose_name=_('user type')
    )
    contact = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('contact number')
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('location')
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('service category')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('description')
    )
    experience = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('years of experience')
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('profile picture')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def clean(self):
        if self.user_type == 'SERVICE_PROVIDER' and not self.category:
            raise ValidationError({'category': 'Category is required for service providers'})
        if self.user_type == 'USER' and self.category:
            raise ValidationError({'category': 'Regular users should not have a category'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

class UserToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('user')
    )
    token = models.CharField(
        max_length=255,
        verbose_name=_('token')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at')
    )

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

    class Meta:
        verbose_name = _('User Token')
        verbose_name_plural = _('User Tokens')
        ordering = ['-created_at']

class Dashboard(models.Model):
    """
    A dummy model for the admin dashboard.
    This model is not meant to be used for storing data.
    """
    class Meta:
        managed = False
        verbose_name_plural = _('Dashboard')
        app_label = 'registration'

    def __str__(self):
        return 'Dashboard'
