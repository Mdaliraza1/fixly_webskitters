from rest_framework import serializers
from .models import Booking
from registration.models import User
from django.utils import timezone
from rest_framework.response import Response
from registration.models import UserToken   
from rest_framework import serializers
from booking.models import Booking
from django.utils import timezone
from datetime import time, date

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        date = data.get('date')
        slot = data.get('time_slot')
        service_provider = data.get('service_provider')
        user = self.context.get('user')

        # ✅ Prevent booking in the past
        today = timezone.localdate()
        if date < today:
            raise serializers.ValidationError("You cannot book a service in the past.")

        # ✅ Validate time slot: on the hour from 10:00 to 17:00
        if slot < time(10, 0) or slot > time(17, 0) or slot.minute != 0 or slot.second != 0:
            raise serializers.ValidationError("Time slot must be on the hour from 10:00 to 17:00.")

        # ✅ Prevent booking yourself
        if user and service_provider and user == service_provider:
            raise serializers.ValidationError("You cannot book yourself as the service provider.")

        # ✅ Prevent double booking
        if Booking.objects.filter(
            service_provider=service_provider,
            date=date,
            time_slot=slot
        ).exists():
            raise serializers.ValidationError("This time slot is already booked.")
        return data
    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        return super().create(validated_data)

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
            if user.user_type != "SERVICE_PROVIDER":
                raise serializers.ValidationError("The provided ID does not belong to a service provider.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Service provider not found.")
        return value

    def validate_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Date cannot be in the past.")
        return value
