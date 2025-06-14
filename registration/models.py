from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone
from service.models import Service

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('USER', 'User'),
        ('SERVICE_PROVIDER', 'Service Provider'),
        ('ADMIN', 'Admin'),
    )

    email = models.EmailField(_('email address'), unique=True)

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
    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ],
        blank=True,
        null=True,
        verbose_name=_('gender')
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('location')
    )
    category = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('service category')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'category']

    def clean(self):
        if self.user_type == 'SERVICE_PROVIDER' and not self.category:
            raise ValidationError({'category': 'Category is required for service providers'})
        if self.user_type == 'USER' and self.category:
            raise ValidationError({'category': 'Regular users should not have a category'})
        if self.user_type == 'ADMIN':
            self.is_staff = True
            self.is_superuser = True

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(default=timezone.now() + timedelta(days=7))


    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

    class Meta:
        ordering = ['-created_at']