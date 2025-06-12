from django.contrib import admin
from django import forms
from .models import Booking, User
from service.models import Service
from django.utils.html import format_html

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_name',
        'get_user_category',
        'get_provider_name',
        'service',
        'date',
        'time_slot',
        'status',
        'created_at',
    )
    list_filter = ('status', 'date', 'service')
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
            'fields': ('service', 'service_provider', 'date', 'time_slot', 'status')
        }),
    )
    readonly_fields = ('user_display', 'user_category_display')

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'User Name'

    def get_user_category(self, obj):
        return obj.user.category
    get_user_category.short_description = 'User Category'

    def get_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
    get_provider_name.short_description = 'Provider Name'

    def user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_display.short_description = "User"

    def user_category_display(self, obj):
        return obj.user.category or "N/A"
    user_category_display.short_description = "User Category"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "service_provider":
            service_id = request.GET.get('service')
            if service_id:
                try:
                    service_obj = Service.objects.get(id=service_id)
                    kwargs["queryset"] = User.objects.filter(
                        user_type="SERVICE_PROVIDER",
                        category=service_obj.category
                    )
                except Service.DoesNotExist:
                    kwargs["queryset"] = User.objects.filter(user_type="SERVICE_PROVIDER")
            else:
                kwargs["queryset"] = User.objects.filter(user_type="SERVICE_PROVIDER")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/jquery.init.js', 'custom/admin_booking.js',)
