from django.contrib import admin
from .models import Review
from utils.admin_actions import export_as_csv_action
from django.utils.html import format_html

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'get_reviewer_name',
        'get_reviewer_email',
        'get_provider_name',
        'get_provider_email',
        'rating_stars',
        'created_at'
    )
    list_filter = ('rating', 'created_at')
    search_fields = (
        'reviewer__email', 'reviewer__first_name', 'reviewer__last_name',
        'service_provider__email', 'service_provider__first_name', 'service_provider__last_name',
        'comment'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = [export_as_csv_action()]

    fieldsets = (
        ('Review Details', {
            'fields': ('reviewer', 'service_provider', 'rating', 'comment')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('reviewer', 'service_provider', 'created_at')
        return ('created_at',)

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    rating_stars.short_description = 'Rating'

    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.first_name} {obj.reviewer.last_name}"
    get_reviewer_name.short_description = 'Reviewer Name'

    def get_reviewer_email(self, obj):
        return obj.reviewer.email
    get_reviewer_email.short_description = 'Reviewer Email'

    def get_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
    get_provider_name.short_description = 'Provider Name'

    def get_provider_email(self, obj):
        return obj.service_provider.email
    get_provider_email.short_description = 'Provider Email'
