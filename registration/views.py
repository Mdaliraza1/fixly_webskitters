from rest_framework import permissions, status, exceptions
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta, timezone
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, UserToken
from .serializers import (
    CustomerRegistrationSerializer, ServiceProviderRegistrationSerializer,
    UserUpdateSerializer, ServiceProviderUpdateSerializer, UserSerializer,ProviderSerializer
)
from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token


# Customer Registration View
class CustomerRegistrationView(APIView):
    def post(self, request):
        user = request.data
        print(f'User data received: {user}')
        
        if User.objects.filter(email=user.get('email')).exists():
            return Response({'error': 'Email already exists!'}, status=400)
        if user.get('password') != user.get('confirm_password'):
            return Response({'error': 'Passwords do not match!'}, status=400)

        serializer = CustomerRegistrationSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Service Provider Registration View
class ServiceProviderRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = request.data
        print(f'User data received: {user}')
        if User.objects.filter(email=user.get('email')).exists():
            return Response({'error': 'Email already exists!'}, status=400)
        if user.get('password') != user.get('confirm_password'):
            return Response({'error': 'Passwords do not match!'}, status=400)
        serializer = ServiceProviderRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# User profile View
class UserAPIView(APIView):
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

        response = Response({
            'user': UserSerializer(user).data,
            'access_token': new_access_token,
            'refresh_token': new_refresh_token
        })
        response.set_cookie(key='refresh_token', value=new_refresh_token, httponly=True)
        return response


# User Update View
class UserUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Service Provider Update View
class ProviderUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = ServiceProviderUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login API
class LoginAPIView(APIView):
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

        UserToken.objects.create(user=user, token=refresh_token, expired_at=timezone.now() + timedelta(days=7))

        response = Response({'message':'Successfully logged in!!','access_token': access_token, 'refresh_token': refresh_token}, status=200)
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True)
        return response


# Refresh Token API
class RefreshAPIView(APIView):
    def post(self, request: Request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=400)

        try:
            user_id = decode_refresh_token(refresh_token)
        except exceptions.AuthenticationFailed as e:
            return Response({'error': str(e)}, status=401)

        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({'error': 'User not found'}, status=404)

        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        UserToken.objects.filter(user=user).delete()  # Remove old refresh token
        UserToken.objects.create(user=user, token=new_refresh_token, expired_at=timezone.now() + timedelta(days=7))

        response = Response({'access_token': new_access_token, 'refresh_token': new_refresh_token}, status=200)
        response.set_cookie(key='refresh_token', value=new_refresh_token, httponly=True, secure=True)
        return response


# Service Provider List View
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


# Logout API
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
