from django.contrib import admin
from .models import Review
from utils.admin_actions import export_as_csv_action
from django.utils.html import format_html

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'service_provider', 'rating_stars', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__email', 'reviewer__first_name', 'reviewer__last_name',
                    'service_provider__email', 'service_provider__first_name', 'service_provider__last_name',
                    'comment')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = [export_as_csv_action()]
    
    fieldsets = (
        ('Review Details', {
            'fields': ('reviewer', 'service_provider', 'rating', 'comment')
        }),
    )
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('reviewer', 'service_provider', 'created_at')
        return ('created_at',)
