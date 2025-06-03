from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserToken

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'contact', 'get_user_type_display', 'category')
    list_filter = ('user_type', 'category')
    search_fields = ('email', 'first_name', 'last_name', 'contact')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'user_type')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'contact', 'gender', 'location')}),
        ('Service Info', {'fields': ('category',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'contact', 'password1', 'password2', 'user_type'),
        }),
    )
    readonly_fields = ('last_login', 'date_joined')

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expired_at')
    search_fields = ('user__email', 'token')
