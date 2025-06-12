from django.contrib import admin
from django import forms
from .models import Booking
from utils.admin_actions import export_as_csv_action


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show full name instead of email for User dropdown
        self.fields['user'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.email})"

        # Show full name instead of email for Provider dropdown
        self.fields['service_provider'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.email})"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm

    list_display = (
        'get_user_name',
        'get_user_email',
        'get_provider_name',
        'get_provider_email',
        'date',
        'time_slot',
        'status',
        'created_at'
    )
    list_filter = ('status', 'date')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'service_provider__email', 'service_provider__first_name', 'service_provider__last_name'
    )
    date_hierarchy = 'date'
    ordering = ('-date', '-time_slot')
    actions = [export_as_csv_action()]

    # Only use fieldsets OR fields (not both to avoid admin.E005)
    fields = ('user', 'service_provider', 'date', 'time_slot', 'status')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing
            return ()
        return ()

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'User Name'

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'

    def get_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
    get_provider_name.short_description = 'Provider Name'

    def get_provider_email(self, obj):
        return obj.service_provider.email
    get_provider_email.short_description = 'Provider Email'
