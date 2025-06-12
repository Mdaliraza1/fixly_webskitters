from django.contrib import admin
from .models import Service
from utils.admin_actions import export_as_csv_action

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('category', 'description', 'price')
    list_filter = ('category',)
    search_fields = ('category', 'description')
    ordering = ('category', 'price')
    actions = [export_as_csv_action()]
    
    fieldsets = (
        ('Service Information', {
            'fields': ('category', 'description', 'price'),
            'classes': ('wide',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('category',)
        return ()
