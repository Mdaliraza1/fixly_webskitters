from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import time
from .models import Booking
from .serializers import BookingSerializer, AvailableSlotsSerializer
from registration.models import User, UserToken
from registration.authentication import decode_refresh_token


def get_user_from_refresh_token(request):
    token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')
    if not token:
        return None, Response({'error': 'Refresh token not provided'}, status=400)

    try:
        user_id = decode_refresh_token(token)
        user = User.objects.get(pk=user_id)
        token_obj = UserToken.objects.filter(user=user, token=token).first()
        if not token_obj:
            return None, Response({'error': 'Invalid or expired refresh token'}, status=401)
        return user, None
    except User.DoesNotExist:
        return None, Response({'error': 'User not found'}, status=404)
    except Exception as e:
        return None, Response({'error': f'Token error: {str(e)}'}, status=401)


class CreateBookingView(APIView):
    def post(self, request):
        # Get user from the refresh token
        user, error_response = get_user_from_refresh_token(request)
        if error_response:
            return error_response

        # Copy the request data to avoid modifying original request data
        data = request.data.copy()

        # Log the request data to see what's being sent
        print(f"Request Data: {data}")

        # Ensure the 'user' field is set
        data['user'] = user.id  # Set the user ID here
        print(f"Data after adding user: {data}")  # Log data after setting 'user'

        # Create the booking serializer
        serializer = BookingSerializer(data=data)

        # Validate and save the serializer
        if serializer.is_valid():
            print("Serializer is valid. Saving booking.")
            serializer.save()  # Save the booking instance with the user field included
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Log serializer errors if validation fails
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserBookingsView(APIView):
    def post(self, request):  # Using POST to send refresh_token
        user, error_response = get_user_from_refresh_token(request)
        if error_response:
            return error_response

        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class ServiceProviderBookingsView(APIView):
    def post(self, request):  # Using POST to send refresh_token
        user, error_response = get_user_from_refresh_token(request)
        if error_response:
            return error_response

        bookings = Booking.objects.filter(service_provider=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class AvailableSlotsView(APIView):
    def post(self, request):  # Using POST to send refresh_token and params
        user, error_response = get_user_from_refresh_token(request)
        if error_response:
            return error_response

        serializer = AvailableSlotsSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            service_provider_id = serializer.validated_data['service_provider_id']
            booked_slots = Booking.objects.filter(
                date=date,
                service_provider_id=service_provider_id
            ).values_list('time_slot', flat=True)

            all_slots = [time(hour=h) for h in range(10, 18)]
            available_slots = [slot.strftime("%H:%M") for slot in all_slots if slot not in booked_slots]

            return Response({'available_slots': available_slots})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
