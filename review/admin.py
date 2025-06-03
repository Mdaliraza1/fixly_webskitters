from django.contrib import admin
from .models import Review
from utils.admin_actions import export_as_csv_action

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'service_provider', 'rating', 'created_at')
    list_filter = ('service_provider',)
    search_fields = ('reviewer__email', 'service_provider__email')
    ordering = ('-created_at',)
    readonly_fields = ('reviewer', 'created_at')
    actions = [export_as_csv_action("Export Reviews as CSV")]
