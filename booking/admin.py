from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_email',
        'get_user_first_name',
        'get_provider_email',
        'get_provider_first_name',
        'date',
        'time_slot',
        'status',
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'service_provider__email', 'service_provider__first_name', 'service_provider__last_name',
        'user__contact', 'user__location',
    )

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    get_user_email.admin_order_field = 'user__email'

    def get_user_first_name(self, obj):
        return obj.user.first_name
    get_user_first_name.short_description = 'User First Name'
    get_user_first_name.admin_order_field = 'user__first_name'

    def get_provider_email(self, obj):
        return obj.service_provider.email
    get_provider_email.short_description = 'Provider Email'
    get_provider_email.admin_order_field = 'service_provider__email'

    def get_provider_first_name(self, obj):
        return obj.service_provider.first_name
    get_provider_first_name.short_description = 'Provider First Name'
    get_provider_first_name.admin_order_field = 'service_provider__first_name'
