from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

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
    """
    A custom authentication form used in the admin app.
    """
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
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        if not user.is_staff:
            raise ValidationError(
                _("This account doesn't have access to the admin. "
                  "Please contact your administrator if you believe this is a mistake."),
                code='not_staff',
            )

    def get_user(self):
        return self.user_cache if hasattr(self, 'user_cache') else None 