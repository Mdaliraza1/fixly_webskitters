
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer, AvailableSlotsSerializer
from registration.models import User
from datetime import time, timedelta, datetime

class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class ServiceProviderBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(service_provider=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class AvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = AvailableSlotsSerializer(data=request.query_params)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            service_provider_id = serializer.validated_data['service_provider_id']
            booked_slots = Booking.objects.filter(date=date, service_provider_id=service_provider_id).values_list('time_slot', flat=True)
            
            all_slots = [time(hour=h) for h in range(10, 18)]
            available_slots = [slot.strftime("%H:%M") for slot in all_slots if slot not in booked_slots]

            return Response({'available_slots': available_slots})
        return Response(serializer.errors, status=400)
