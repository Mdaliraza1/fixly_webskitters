from django.contrib import admin
from .models import Booking
from utils.admin_actions import export_as_csv_action

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_provider', 'date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'service_provider', 'date')
    search_fields = ('user__email', 'service_provider__email')
    ordering = ('-created_at',)
    list_editable = ('service_provider', 'status', 'time_slot')
    actions = [export_as_csv_action("Export Bookings as CSV")]


