from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'category', 'description', 'experience', 'profile_picture')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'category', 'description', 'experience', 'profile_picture', 'is_active', 'is_staff', 'is_superuser') 