from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone

from .serializers import (
    CustomerRegistrationSerializer, ServiceProviderRegistrationSerializer,
    UserUpdateSerializer, ServiceProviderUpdateSerializer,
    UserSerializer, ProviderSerializer
)

User = get_user_model()

def create_admin():
    try:
        # Check if admin already exists
        if User.objects.filter(email='admin@example.com').exists():
            return {'status': 'error', 'message': 'Admin user already exists'}
        
        # Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            user_type='ADMIN',
            is_staff=True,
            is_superuser=True
        )
        admin.save()
        return {'status': 'success', 'message': 'Admin user created successfully'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def create_admin_view(request):
    result = create_admin()
    return JsonResponse(result)

def index(request):
    if request.path == '/':
        return render(request, 'index.html')
    return redirect('admin:login')

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    subject = 'Your Fixly Registration OTP'
    html_message = render_to_string('registration/email/otp_email.html', {
        'otp': otp,
        'email': email,
        'year': timezone.now().year
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

class CustomerRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return Response({
                    'error': 'Email already registered.'
                }, status=status.HTTP_400_BAD_REQUEST)

            otp = generate_otp()
            
            # Store OTP in cache with 10 minutes expiration
            cache_key = f'registration_otp_{email}'
            cache.set(cache_key, {
                'otp': otp,
                'data': serializer.validated_data
            }, timeout=600)  # 10 minutes

            # Send OTP via email
            if send_otp_email(email, otp):
                return Response({
                    'message': 'OTP sent to your email.',
                    'email': email,
                    'expires_in': 600  # 10 minutes in seconds
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to send OTP. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({
                'error': 'Email and OTP are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get stored OTP and data from cache
        cache_key = f'registration_otp_{email}'
        stored_data = cache.get(cache_key)

        if not stored_data:
            return Response({
                'error': 'OTP expired or invalid. Please request a new OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if otp != stored_data['otp']:
            return Response({
                'error': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user
            user = User.objects.create_user(
                username=stored_data['data']['email'],
                email=stored_data['data']['email'],
                password=stored_data['data']['password'],
                first_name=stored_data['data']['first_name'],
                last_name=stored_data['data']['last_name'],
                contact=stored_data['data']['contact'],
                gender=stored_data['data']['gender'],
                user_type='USER'
            )

            # Clear OTP from cache
            cache.delete(cache_key)

            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully.',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': f'Failed to create user: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if there's an existing OTP request
        cache_key = f'registration_otp_{email}'
        stored_data = cache.get(cache_key)
        
        if stored_data:
            # Check if enough time has passed (1 minute cooldown)
            if cache.ttl(cache_key) > 540:  # 9 minutes (allowing 1 minute cooldown)
                return Response({
                    'error': 'Please wait before requesting a new OTP.'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate new OTP
        otp = generate_otp()
        
        # Store new OTP in cache
        cache.set(cache_key, {
            'otp': otp,
            'data': stored_data['data'] if stored_data else None
        }, timeout=600)  # 10 minutes

        # Send new OTP
        if send_otp_email(email, otp):
            return Response({
                'message': 'New OTP sent to your email.',
                'email': email,
                'expires_in': 600
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to send OTP. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceProviderRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ServiceProviderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return Response({
                    'error': 'Email already registered.'
                }, status=status.HTTP_400_BAD_REQUEST)

            otp = generate_otp()
            
            # Store OTP in cache with 10 minutes expiration
            cache_key = f'provider_registration_otp_{email}'
            cache.set(cache_key, {
                'otp': otp,
                'data': serializer.validated_data
            }, timeout=600)  # 10 minutes

            # Send OTP via email
            if send_otp_email(email, otp):
                return Response({
                    'message': 'OTP sent to your email.',
                    'email': email,
                    'expires_in': 600  # 10 minutes in seconds
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to send OTP. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateProviderOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({
                'error': 'Email and OTP are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get stored OTP and data from cache
        cache_key = f'provider_registration_otp_{email}'
        stored_data = cache.get(cache_key)

        if not stored_data:
            return Response({
                'error': 'OTP expired or invalid. Please request a new OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if otp != stored_data['otp']:
            return Response({
                'error': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create provider user
            user = User.objects.create_user(
                username=stored_data['data']['email'],
                email=stored_data['data']['email'],
                password=stored_data['data']['password'],
                first_name=stored_data['data']['first_name'],
                last_name=stored_data['data']['last_name'],
                contact=stored_data['data']['contact'],
                gender=stored_data['data']['gender'],
                user_type='PROVIDER'
            )

            # Create provider profile
            provider = ServiceProvider.objects.create(
                user=user,
                category=stored_data['data']['category'],
                experience=stored_data['data']['experience'],
                hourly_rate=stored_data['data']['hourly_rate'],
                availability=stored_data['data']['availability'],
                description=stored_data['data']['description']
            )

            # Clear OTP from cache
            cache.delete(cache_key)

            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Service provider registered successfully.',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type
                },
                'provider': {
                    'id': provider.id,
                    'category': provider.category,
                    'experience': provider.experience,
                    'hourly_rate': provider.hourly_rate,
                    'availability': provider.availability
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': f'Failed to create service provider: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResendProviderOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if there's an existing OTP request
        cache_key = f'provider_registration_otp_{email}'
        stored_data = cache.get(cache_key)
        
        if stored_data:
            # Check if enough time has passed (1 minute cooldown)
            if cache.ttl(cache_key) > 540:  # 9 minutes (allowing 1 minute cooldown)
                return Response({
                    'error': 'Please wait before requesting a new OTP.'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate new OTP
        otp = generate_otp()
        
        # Store new OTP in cache
        cache.set(cache_key, {
            'otp': otp,
            'data': stored_data['data'] if stored_data else None
        }, timeout=600)  # 10 minutes

        # Send new OTP
        if send_otp_email(email, otp):
            return Response({
                'message': 'New OTP sent to your email.',
                'email': email,
                'expires_in': 600
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to send OTP. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                response.data['user_type'] = user.user_type
                response.data['user_id'] = user.id
        return response

class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'error': 'Invalid token or already logged out.'}, status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data, 'is_admin': request.user.is_superuser}, status=status.HTTP_200_OK)

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        if user.user_type != 'USER':
            return Response({'error': 'Only customers can access this route.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Customer profile updated successfully.', 'user': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProviderUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        if user.user_type != 'SERVICE_PROVIDER':
            return Response({'error': 'Only service providers can access this route.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ServiceProviderUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Service provider profile updated successfully.', 'provider': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceProviderListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = {'user_type': 'SERVICE_PROVIDER'}
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        if category:
            filters['category'] = category
        if location:
            filters['location'] = location

        queryset = User.objects.filter(**filters)
        serializer = ProviderSerializer(queryset, many=True)
        return Response({'providers': serializer.data}, status=status.HTTP_200_OK)

def get_category_name(user):
    if user.category:  # New ForeignKey
        return user.category.category
    elif user.legacy_category:  # Old CharField
        return user.legacy_category
    return '-'