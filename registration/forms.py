from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
import re
from service.models import Service

def validate_email_format(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationError("Invalid email format.")
    return email

def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must include at least one uppercase letter.")
    if not re.search(r"[,\./\?;'!@#$%&*~]", password):
        raise ValidationError("Password must include at least one special character.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must include at least one lowercase letter.")
    if not re.search(r'\d', password):
        raise ValidationError("Password must include at least one digit.")
    return password

def validate_contact_format(contact):
    if not re.fullmatch(r'[6-9]\d{9}', contact):
        raise ValidationError("Contact number must be a valid 10-digit Indian mobile number.")
    return contact

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.fields:
            self.fields['category'].queryset = Service.objects.all()

    def clean_email(self):
        return validate_email_format(self.cleaned_data['email'])

    def clean_password1(self):
        return validate_password_strength(self.cleaned_data['password1'])

    def clean_contact(self):
        return validate_contact_format(self.cleaned_data['contact'])

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'category', 'gender', 'is_active', 'is_staff', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.fields:
            self.fields['category'].queryset = Service.objects.all()

    def clean_email(self):
        return validate_email_format(self.cleaned_data['email'])

    def clean_contact(self):
        return validate_contact_format(self.cleaned_data['contact'])

class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    error_messages = {
        **AdminAuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive. Also ensure you have staff privileges."
        ),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'], code='inactive')
        if not user.is_staff:
            raise ValidationError(
                _("This account doesn't have access to the admin. "
                  "Please contact your administrator if you believe this is a mistake."),
                code='not_staff',
            )

    def get_user(self):
        return self.user_cache if hasattr(self, 'user_cache') else None
