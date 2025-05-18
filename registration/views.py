from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction

from .models import User, UserToken
from .serializers import (
    CustomerRegistrationSerializer, 
    ServiceProviderRegistrationSerializer,
    UserUpdateSerializer, 
    ServiceProviderUpdateSerializer, 
    UserSerializer, 
    ProviderSerializer
)
from .authentication import (
    JWTAuthentication, 
    create_access_token, 
    create_refresh_token, 
    decode_refresh_token
)

# Index View (optional frontend landing)
def index(request):
    return render(request, 'index.html')


# ---------------------- Registration Views ---------------------- #

# Customer Registration
class CustomerRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_data = request.data
        print(f'Customer data received: {user_data}')
        
        if User.objects.filter(email=user_data.get('email')).exists():
            return Response({'error': 'Email already exists!'}, status=400)

        if user_data.get('password') != user_data.get('confirm_password'):
            return Response({'error': 'Passwords do not match!'}, status=400)

        serializer = CustomerRegistrationSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Service Provider Registration
class ServiceProviderRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_data = request.data
        print(f'Provider data received: {user_data}')

        if User.objects.filter(email=user_data.get('email')).exists():
            return Response({'error': 'Email already exists!'}, status=400)

        if user_data.get('password') != user_data.get('confirm_password'):
            return Response({'error': 'Passwords do not match!'}, status=400)

        serializer = ServiceProviderRegistrationSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------------------- Login and Logout ---------------------- #

# Login View
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=401)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        UserToken.objects.create(
            user=user,
            token=refresh_token,
            expired_at=timezone.now() + timedelta(days=7)
        )

        response = Response({
            'message': 'Successfully logged in!',
            'access_token': access_token,
            'refresh_token': refresh_token
        }, status=200)
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True)
        return response


# Logout View
@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(APIView):
    def post(self, request: Request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token missing'}, status=400)

        UserToken.objects.filter(token=refresh_token).delete()

        response = Response({'status': 'success', 'message': 'Logged out successfully'}, status=200)
        response.delete_cookie(key='refresh_token')
        return response


# ---------------------- Token Refresh ---------------------- #

# Refresh Access Token
class RefreshAPIView(APIView):
    def post(self, request: Request):
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

        token_obj.delete()

        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        UserToken.objects.create(
            user=user,
            token=new_refresh_token,
            expired_at=timezone.now() + timedelta(days=7)
        )

        response = Response({
            'user': UserSerializer(user).data,
            'access_token': new_access_token,
            'refresh_token': new_refresh_token
        }, status=200)
        response.set_cookie(key='refresh_token', value=new_refresh_token, httponly=True)
        return response


# ---------------------- User Profile ---------------------- #

# Authenticated User Profile View
class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_admin = request.auth.get('is_admin', False)
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'is_admin': is_admin
        })


# ---------------------- User Update Views ---------------------- #

# Base Update View for User and Provider
class BaseUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @transaction.atomic
    def patch(self, request: Request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Invalidate old refresh tokens
            UserToken.objects.filter(user=user, expired_at__gt=timezone.now()).update(expired_at=timezone.now())

            # Generate new tokens
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)

            UserToken.objects.create(
                user=user,
                token=refresh_token,
                expired_at=timezone.now() + timedelta(days=7)
            )

            return Response({
                'user': serializer.data,
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Update View (Customer)
class UserUpdateView(BaseUpdateView):
    serializer_class = UserUpdateSerializer


# Service Provider Update View
class ProviderUpdateView(BaseUpdateView):
    serializer_class = ServiceProviderUpdateSerializer


# ---------------------- Service Provider List ---------------------- #

# List & Filter Providers
class ServiceProviderListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        queryset = User.objects.filter(user_type='SERVICE_PROVIDER')
        category = request.query_params.get('category')
        location = request.query_params.get('location')

        if category:
            queryset = queryset.filter(category=category)
        if location:
            queryset = queryset.filter(location=location)

        serializer = ProviderSerializer(queryset, many=True)
        return Response(serializer.data)
