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
        user = get_user_from_refresh_token(request)
        if user.user_type == "Service_provider":
            return Response(
                {"detail": "You are not allowed to access this resource as a service provider."},
                status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        print(f"Payload: {data}")  

        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            print("Serializer is valid. Saving booking.")
            serializer.save(user=user) 
            return Response(serializer.data,  status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserBookingsView(APIView):
    def post(self, request):  # Using POST to send refresh_token
        user, error_response = get_user_from_refresh_token(request)
        if error_response:
            return error_response

        if user.user_type == "SERVICE_POVIDER":
            return Response(
                {"detail": "You are not allowed to access this resource as a service provider."},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(
            {
                "message": "Booking retrieved successfully",
                "bookings": serializer.data
            },
            status=status.HTTP_200_OK
        )


class ServiceProviderBookingsView(APIView):
    def post(self, request):  # Using POST to send refresh_token
        user, error_response = get_user_from_refresh_token(request)
        if error_response:
            return error_response

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
    def post(self, request):  # Using POST to send refresh_token and params
        user, error_response = get_user_from_refresh_token(request)
        if error_response:
            return error_response

        serializer = AvailableSlotsSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            service_provider_id = serializer.validated_data['service_provider_id']

            # Fetch already booked 1-hour slots
            booked_slots = list(Booking.objects.filter(
                date=date,
                service_provider_id=service_provider_id
            ).values_list('time_slot', flat=True))

            # Define 1-hour slots: 10:00 AM to 6:00 PM (last slot at 5 PM to 6 PM)
            all_slots = [time(hour=h) for h in range(10, 18)]

            # Filter out booked ones
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