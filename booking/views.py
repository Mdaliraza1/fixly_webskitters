
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer, AvailableSlotsSerializer
from registration.models import User,UserToken
from datetime import time,timezone,timedelta
from registration.authentication import decode_refresh_token,create_access_token,create_refresh_token

class CreateBookingView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=400)
        try:
            user_id = decode_refresh_token(refresh_token)
            user = User.objects.get(pk=user_id)

            token_obj = UserToken.objects.filter(
                user=user,
                token=refresh_token,
                expired_at__gt=timezone.now()
            ).first()
            if not token_obj:
                return Response({'error': 'Invalid or expired refresh token'}, status=401)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=401)
        # Invalidate the old token
        token_obj.delete()

        # Generate new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        # Save new refresh token
        UserToken.objects.create(
            user=user,
            token=new_refresh_token,
            expired_at=timezone.now() + timedelta(days=7)
        )
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(User=request.user)
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
