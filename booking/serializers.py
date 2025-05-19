from rest_framework import serializers
from .models import Booking
from registration.models import User
from django.utils import timezone
from rest_framework.response import Response
from registration.authentication import decode_refresh_token 
from registration.models import UserToken   
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        # Validate time slot: must be on the hour from 10:00 to 17:00 (last booking 5-6pm)
        slot = data.get('time_slot')
        if slot.hour < 10 or slot.hour > 17 or slot.minute != 0 or slot.second != 0:
            raise serializers.ValidationError("Time slot must be on the hour from 10:00 to 17:00.")

        # Prevent user from booking themselves as service provider
        user = self.context.get('user') or self.initial_data.get('user')
        service_provider = data.get('service_provider')
        if user and service_provider and user == service_provider:
            raise serializers.ValidationError("You cannot book yourself as the service provider.")

        # Check if this slot is already booked
        if Booking.objects.filter(
            service_provider=service_provider,
            date=data.get('date'),
            time_slot=slot
        ).exists():
            raise serializers.ValidationError("This time slot is already booked.")

        return data

from rest_framework import serializers
from .models import Booking

class UserBookingSerializer(serializers.ModelSerializer):
    service_provider_id = serializers.IntegerField(source='service_provider.id')
    service_provider_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'date',
            'time_slot',
            'service_provider_id',
            'service_provider_name',
        ]

    def get_service_provider_name(self, obj):
        provider = obj.service_provider
        if provider:
            return f"{provider.first_name} {provider.last_name}"
        return None

class ProviderBookingSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source='user.id')
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'date',
            'time_slot',
            'customer_id',
            'customer_name',
        ]

    def get_customer_name(self, obj):
        customer = obj.user
        if customer:
            return f"{customer.first_name} {customer.last_name}"
        return None
class AvailableSlotsSerializer(serializers.Serializer):
    date = serializers.DateField()
    service_provider_id = serializers.IntegerField()

    def validate_service_provider_id(self, value):
        try:
            user = User.objects.get(pk=value)
            # Assuming user_type is a field to distinguish service providers from customers
            if user.user_type != "SERVICE_PROVIDER":
                raise serializers.ValidationError("The provided ID is not a valid service provider.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Service provider not found.")
        return value
