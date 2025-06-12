from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'category')
        exclude = ('groups', 'user_permissions')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'category', 'description', 'experience', 'profile_picture', 'is_active', 'is_staff', 'is_superuser')
        exclude = ('groups', 'user_permissions')

class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data 