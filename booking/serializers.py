from rest_framework import serializers
from .models import Booking
from registration.models import User

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user']  # So 'user' is not required in input

class AvailableSlotsSerializer(serializers.Serializer):
    date = serializers.DateField()
    service_provider_id = serializers.IntegerField()
