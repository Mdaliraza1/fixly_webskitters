from django.contrib import admin
from django import forms
from .models import Booking, User


class ProviderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Clean title case + remove weird tuple-like display
        return f"{obj.first_name.title()} {obj.last_name.title()} ({obj.category}, {obj.location})"


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['service_provider'] = ProviderChoiceField(
            queryset=User.objects.filter(user_type='SERVICE_PROVIDER'),
            label='Service Provider'
        )

        instance = self.instance

        # Prevent same person as both user and provider
        if instance and instance.pk:
            if instance.user_id != instance.service_provider_id:
                self.fields['user'].queryset = self.fields['user'].queryset.exclude(id=instance.service_provider.id)
        self.fields['service_provider'].queryset = self.fields['service_provider'].queryset.exclude(id=instance.user.id)


        # Exclude already booked providers for selected date/time
        if 'date' in self.data and 'time_slot' in self.data:
            try:
                date = self.data.get('date')
                time_slot = self.data.get('time_slot')

                if date and time_slot:
                    booked_providers = Booking.objects.filter(
                        date=date,
                        time_slot=time_slot
                    ).exclude(id=instance.id).values_list('service_provider_id', flat=True)

                    self.fields['service_provider'].queryset = self.fields['service_provider'].queryset.exclude(
                        id__in=booked_providers
                    )
            except Exception:
                pass  # Handle early validation stages
        elif instance and instance.pk:
            # On editing, don't allow assigning a provider already booked at same slot
            booked_providers = Booking.objects.filter(
                date=instance.date,
                time_slot=instance.time_slot
            ).exclude(id=instance.id).values_list('service_provider_id', flat=True)

            self.fields['service_provider'].queryset = self.fields['service_provider'].queryset.exclude(
                id__in=booked_providers
            )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm

    list_display = (
        'get_user_name',
        'get_user_email',
        'get_provider_name_with_location',  # updated to be more readable
        'get_provider_email',
        'date',
        'time_slot',
        'status',
        'created_at',
    )

    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'service_provider__email', 'service_provider__first_name', 'service_provider__last_name',
        'user__contact', 'user__location',
    )

    def get_user_name(self, obj):
        return f"{obj.user.first_name.title()} {obj.user.last_name.title()}"
    get_user_name.short_description = "User Name"

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "User Email"

    def get_provider_name_with_location(self, obj):
        return f"{obj.service_provider.first_name.title()} {obj.service_provider.last_name.title()} ({obj.service_provider.category}, {obj.service_provider.location})"
    get_provider_name_with_location.short_description = "Service Provider"

    def get_provider_email(self, obj):
        return obj.service_provider.email
    get_provider_email.short_description = "Provider Email"
