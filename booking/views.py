from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import time, date
from django.db import IntegrityError

from registration.models import User, UserToken
from registration.authentication import decode_refresh_token

from .models import Booking
from .serializers import (
    BookingSerializer,
    AvailableSlotsSerializer,
    UserBookingSerializer,
    ProviderBookingSerializer,
    UpdateBookingStatusSerializer,
)


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

        if user.user_type != "CUSTOMER":
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
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateBookingStatusView(APIView):
    def put(self, request, pk):
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

        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only service provider who owns the booking can update its status
        if booking.service_provider != user:
            return Response({"detail": "You do not have permission to update this booking."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateBookingStatusSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Booking status updated successfully", "booking": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
