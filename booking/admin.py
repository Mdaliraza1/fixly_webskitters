from django import forms
from .models import Booking, User

class ProviderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name} ({obj.category}, {obj.location})"


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'service_provider', 'service', 'date', 'time_slot', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance

        # ✅ Lock user field to just current booking's user
        if instance and instance.pk:
            self.fields['user'].queryset = User.objects.filter(id=instance.user_id)
            self.fields['user'].disabled = True  # Make user field read-only

        # ✅ Label providers properly
        self.fields['service_provider'] = ProviderChoiceField(
            queryset=User.objects.filter(user_type='SERVICE_PROVIDER'),
            label='Service Provider'
        )

        # ✅ Exclude already booked providers on same date/time
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
                pass
        elif instance and instance.pk:
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
        'user_name',
        'user_email',
        'provider_name',
        'provider_email',
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

    readonly_fields = ('user',)  # ✅ also mark as read-only in admin

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_user_email(self, obj):
        return obj.user.email

    def get_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name} ({obj.service_provider.category}, {obj.service_provider.location})"

    def get_provider_email(self, obj):
        return obj.service_provider.email
