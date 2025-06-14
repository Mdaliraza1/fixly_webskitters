from django import forms
from django.contrib import admin
from .models import Booking
from registration.models import User
from service.models import Service
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone


class ProviderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Get the category name from Service model
        service = Service.objects.filter(category=obj.category).first()
        if service:
            category_display = service.category
        else:
            # If no service found, try to get a valid category name
            valid_categories = ['Plumber', 'Carpenter', 'Electrician', 'Cleaning']
            if obj.category in valid_categories:
                category_display = obj.category
            else:
                # If category is a number, try to map it to a valid category
                try:
                    category_index = int(obj.category) - 1
                    if 0 <= category_index < len(valid_categories):
                        category_display = valid_categories[category_index]
                    else:
                        category_display = obj.category
                except (ValueError, TypeError):
                    category_display = obj.category
        return f"{obj.first_name} {obj.last_name} ({category_display}, {obj.location})"


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'service_provider', 'date', 'time_slot', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance

        # Initialize user field first
        self.fields['user'] = forms.ModelChoiceField(
            queryset=User.objects.filter(user_type='USER'),
            label='User'
        )

        # Initialize service provider field with proper category display
        self.fields['service_provider'] = ProviderChoiceField(
            queryset=User.objects.filter(user_type='SERVICE_PROVIDER'),
            label='Service Provider'
        )

        # Handle user field for existing bookings
        if instance and instance.pk and hasattr(instance, 'user_id'):
            self.fields['user'].queryset = User.objects.filter(id=instance.user_id)
            self.fields['user'].disabled = True

        # Only filter providers if both date and time slot are provided
        if 'date' in self.data and 'time_slot' in self.data and self.data.get('date') and self.data.get('time_slot'):
            try:
                date = self.data.get('date')
                time_slot = self.data.get('time_slot')
                booked_providers = Booking.objects.filter(
                    date=date,
                    time_slot=time_slot
                ).exclude(id=instance.id if instance and instance.pk else None).values_list('service_provider_id', flat=True)
                self.fields['service_provider'].queryset = self.fields['service_provider'].queryset.exclude(
                    id__in=booked_providers
                )
            except Exception:
                pass
        elif instance and instance.pk and instance.date and instance.time_slot:
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
        'get_provider_name',
        'get_provider_category',
        'get_provider_email',
        'date',
        'time_slot',
        'status',
        'created_at',
    )

    list_filter = ('status',)

    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'service_provider__email', 'service_provider__first_name', 'service_provider__last_name',
        'user__contact', 'user__location',
    )

    # Remove 'user' from readonly_fields to make it editable
    # readonly_fields = ('user',)

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = "User Name"

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "User Email"

    def get_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
    get_provider_name.short_description = "Provider Name"

    def get_provider_category(self, obj):
        # Get the category name from Service model
        if obj.service_provider.category:
            return obj.service_provider.category.category
        return '-'
    get_provider_category.short_description = "Provider Category"

    def get_provider_email(self, obj):
        return obj.service_provider.email
    get_provider_email.short_description = "Provider Email"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Send confirmation email after booking is created or edited
        subject = 'Booking Confirmation - Fixly'
        action = 'updated' if change else 'created'
        context = {
            'user': obj.user,
            'booking': obj,
            'action': action,
            'year': timezone.now().year,
        }
        html_message = render_to_string('booking/email/booking_confirmation.html', context)
        from django.utils.html import strip_tags
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [obj.user.email],
            html_message=html_message,
            fail_silently=True,
        )
