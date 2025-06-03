from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer_info', 'provider_info', 'rating', 'comment', 'created_at')
    search_fields = (
        'reviewer__first_name', 'reviewer__last_name', 'reviewer__email',
        'service_provider__first_name', 'service_provider__last_name', 'service_provider__email',
        'comment'
    )
    list_filter = ('rating', 'created_at', 'service_provider__category')

    def reviewer_info(self, obj):
        return f"{obj.reviewer.first_name} {obj.reviewer.last_name} ({obj.reviewer.email})"
    reviewer_info.short_description = 'Reviewer'

    def provider_info(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name} ({obj.service_provider.email})"
    provider_info.short_description = 'Service Provider'

admin.site.register(Review, ReviewAdmin)
