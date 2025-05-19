from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import time
from django.db import IntegrityError

from registration.models import User, UserToken
from registration.authentication import decode_refresh_token

from .models import Booking
from .serializers import BookingSerializer, AvailableSlotsSerializer


class CreateBookingView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=400)

        try:
            user_id = decode_refresh_token(refresh_token)
            user = User.objects.filter(pk=user_id).first()
            token_obj = UserToken.objects.filter(
                user=user,
                token=refresh_token,
                expired_at__gt=timezone.now()
            ).first()
            if not user or not token_obj:
                return Response({'error': 'User not found or token expired'}, status=404)
        except Exception as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=401)

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
    def post(self, request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=400)

        try:
            user_id = decode_refresh_token(refresh_token)
            user = User.objects.filter(pk=user_id).first()
            token_obj = UserToken.objects.filter(
                user=user,
                token=refresh_token,
                expired_at__gt=timezone.now()
            ).first()
            if not user or not token_obj:
                return Response({'error': 'User not found or token expired'}, status=404)
        except Exception as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=401)

        if user.user_type == "SERVICE_PROVIDER":
            return Response(
                {"detail": "You are not allowed to access this resource as a service provider."},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(
            {
                "message": "Bookings retrieved successfully",
                "bookings": serializer.data
            },
            status=status.HTTP_200_OK
        )


class ServiceProviderBookingsView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=400)

        try:
            user_id = decode_refresh_token(refresh_token)
            user = User.objects.filter(pk=user_id).first()
            token_obj = UserToken.objects.filter(
                user=user,
                token=refresh_token,
                expired_at__gt=timezone.now()
            ).first()
            if not user or not token_obj:
                return Response({'error': 'User not found or token expired'}, status=404)
        except Exception as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=401)

        if user.user_type == "CUSTOMER":
            return Response(
                {"detail": "You are not allowed to access this resource as a Customer."},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects.filter(service_provider=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(
            {
                "message": "Bookings retrieved successfully",
                "bookings": serializer.data
            },
            status=status.HTTP_200_OK
        )


class AvailableSlotsView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=400)

        try:
            user_id = decode_refresh_token(refresh_token)
            user = User.objects.filter(pk=user_id).first()
            token_obj = UserToken.objects.filter(
                user=user,
                token=refresh_token,
                expired_at__gt=timezone.now()
            ).first()
            if not user or not token_obj:
                return Response({'error': 'User not found or token expired'}, status=404)
        except Exception as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=401)

        serializer = AvailableSlotsSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            service_provider_id = serializer.validated_data['service_provider_id']

            # Fetch already booked 1-hour slots
            booked_slots = list(Booking.objects.filter(
                date=date,
                service_provider_id=service_provider_id
            ).values_list('time_slot', flat=True))

            # Define 1-hour slots: 10:00 AM to 6:00 PM (last slot 5-6 PM)
            all_slots = [time(hour=h) for h in range(10, 18)]

            # Filter out booked slots
            available_slots = [
                slot.strftime("%H:%M") for slot in all_slots if slot not in booked_slots
            ]

            return Response(
                {
                    "message": "Available slots retrieved successfully",
                    "available_slots": available_slots
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
