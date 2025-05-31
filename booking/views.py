from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import time
from django.db import IntegrityError

from registration.models import User
from .models import Booking
from .serializers import (
    BookingSerializer,
    AvailableSlotsSerializer,
    UserBookingSerializer,
    ProviderBookingSerializer,
    UpdateBookingStatusSerializer,
)

class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.user_type != "USER":
            return Response(
                {"detail": "You are not allowed to access this resource as a service provider."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        serializer = BookingSerializer(data=data, context={'user': user})
        if serializer.is_valid():
            try:
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'detail': 'This time slot is already booked.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != "USER":
            return Response(
                {"detail": "You are not allowed to access this resource as a service provider."},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects.filter(user=user)
        serializer = UserBookingSerializer(bookings, many=True)

        return Response(
            {
                "message": "Bookings retrieved successfully",
                "bookings": serializer.data
            },
            status=status.HTTP_200_OK
        )


class ServiceProviderBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != "SERVICE_PROVIDER":
            return Response(
                {"detail": "You are not allowed to access this resource as a Customer."},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects.filter(service_provider=user)
        serializer = ProviderBookingSerializer(bookings, many=True)
        return Response(
            {
                "message": "Bookings retrieved successfully",
                "bookings": serializer.data
            },
            status=status.HTTP_200_OK
        )


class AvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AvailableSlotsSerializer(data=request.data)
        if serializer.is_valid():
            date_value = serializer.validated_data['date']
            service_provider_id = serializer.validated_data['service_provider_id']

            all_slots = [time(h, 0) for h in range(10, 18)]
            booked_slots = Booking.objects.filter(
                service_provider_id=service_provider_id,
                date=date_value
            ).values_list('time_slot', flat=True)

            available_slots = [slot.strftime('%H:%M') for slot in all_slots if slot not in booked_slots]

            return Response({
                "available_slots": available_slots
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateBookingStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = request.user

        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        if booking.service_provider != user:
            return Response({"detail": "You do not have permission to update this booking."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateBookingStatusSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Booking status updated successfully", "booking": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
