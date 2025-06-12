from django.contrib import admin
from .models import Booking, User

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
        'created_at',
    )
    list_filter = ('status', 'date')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'service_provider__email', 'service_provider__first_name', 'service_provider__last_name'
    )
    date_hierarchy = 'date'
    ordering = ('-date', '-time_slot')

    fieldsets = (
        ('User Info', {
            'fields': ('user_display', 'user_category_display')
        }),
        ('Booking Info', {
            'fields': ('user', 'service_provider', 'date', 'time_slot', 'status')
        }),
    )
    readonly_fields = ('user_display', 'user_category_display')

    # Custom display methods
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'User Name'

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'

    def get_user_category(self, obj):
        return obj.user.category
    get_user_category.short_description = 'User Category'

    def get_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
    get_provider_name.short_description = 'Provider Name'

    def get_provider_email(self, obj):
        return obj.service_provider.email
    get_provider_email.short_description = 'Provider Email'

    def user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_display.short_description = "User"

    def user_category_display(self, obj):
        return obj.user.category or "N/A"
    user_category_display.short_description = "User Category"
