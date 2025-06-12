from django.contrib import admin
from .models import Booking
from utils.admin_actions import export_as_csv_action

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_provider', 'date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name',
                    'service_provider__email', 'service_provider__first_name', 'service_provider__last_name')
    date_hierarchy = 'date'
    ordering = ('-date', '-time_slot')
    actions = [export_as_csv_action()]
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('user', 'service_provider', 'date', 'time_slot')
        }),
        ('Status Information', {
            'fields': ('status',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user', 'service_provider', 'date', 'time_slot')
        return ()
