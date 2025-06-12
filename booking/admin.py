from django.contrib import admin
from .models import Booking
from registration.models import User
from utils.admin_actions import export_as_csv_action

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_name',
        'get_user_email',
        'get_provider_name',
        'get_provider_email',
        'date',
        'time_slot',
        'status',
        'created_at'
    )
    list_filter = ('status', 'date')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'service_provider__email', 'service_provider__first_name', 'service_provider__last_name'
    )
    date_hierarchy = 'date'
    ordering = ('-date', '-time_slot')
    actions = [export_as_csv_action()]

    # Editable fields in admin form
    fieldsets = (
        ('Booking Details', {
            'fields': ('user', 'service', 'service_provider', 'date', 'time_slot')
        }),
        ('Status Information', {
            'fields': ('status',),
            'classes': ('collapse',)
        }),
    )

    # Allow editing fields even for existing bookings
    fields = ('user', 'service', 'service_provider', 'date', 'time_slot', 'status')

    # Optional: Only show SERVICE_PROVIDER in provider dropdown
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "service_provider":
            kwargs["queryset"] = User.objects.filter(user_type="SERVICE_PROVIDER")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Display helpers
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'User Name'

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'

    def get_provider_name(self, obj):
        if obj.service_provider:
            return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
        return "-"
    get_provider_name.short_description = 'Provider Name'

    def get_provider_email(self, obj):
        return obj.service_provider.email if obj.service_provider else "-"
    get_provider_email.short_description = 'Provider Email'
