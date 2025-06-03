from django.contrib import admin
from .models import Booking
from utils.admin_actions import export_as_csv_action

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'service_provider_name', 'date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'service_provider', 'date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name',
                     'service_provider__email', 'service_provider__first_name', 'service_provider__last_name')
    ordering = ('-created_at',)
    list_editable = ('service_provider', 'status', 'time_slot')
    actions = [export_as_csv_action("Export Bookings as CSV")]

    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.admin_order_field = 'user__first_name'
    user_name.short_description = 'User Name'

    def service_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
    service_provider_name.admin_order_field = 'service_provider__first_name'
    service_provider_name.short_description = 'Service Provider Name'
