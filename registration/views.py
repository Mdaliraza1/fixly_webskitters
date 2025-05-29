from rest_framework import permissions, status
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .models import User, UserToken
from .serializers import (
    CustomerRegistrationSerializer, ServiceProviderRegistrationSerializer,
    UserUpdateSerializer, ServiceProviderUpdateSerializer, UserSerializer, ProviderSerializer
)
from .authentication import create_access_token, create_refresh_token, decode_refresh_token

def index(request):
    return render(request, 'index.html')

def get_user_from_refresh_token(request):
    token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')
    if not token:
        raise ValueError('Refresh token required')
    user_id = decode_refresh_token(token)
    user = User.objects.get(pk=user_id)
    return user, token

class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ServiceProviderRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ServiceProviderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(APIView):
    def post(self, request):
        try:
            user, _ = get_user_from_refresh_token(request)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(user)
        return Response({'user': serializer.data, 'is_admin': user.is_superuser}, status=status.HTTP_200_OK)

class UserUpdateView(APIView):
    def patch(self, request):
        try:
            user, _ = get_user_from_refresh_token(request)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        if user.user_type != 'USER':
            return Response({'error': 'Only customers can access this route.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Customer profile updated successfully.', 'user': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProviderUpdateView(APIView):
    def patch(self, request):
        try:
            user, _ = get_user_from_refresh_token(request)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        if user.user_type != 'SERVICE_PROVIDER':
            return Response({'error': 'Only service providers can access this route.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ServiceProviderUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Service provider profile updated successfully.', 'user': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    def post(self, request: Request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        UserToken.objects.create(user=user, token=refresh_token, expired_at=timezone.now() + timedelta(days=7))

        secure_flag = not settings.DEBUG
        response = Response({
            'message': 'Successfully logged in!',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_type': user.user_type,
        }, status=status.HTTP_200_OK)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=secure_flag,
            samesite='None'
        )
        return response

@method_decorator(csrf_exempt, name='dispatch')
class RefreshAPIView(APIView):
    def post(self, request: Request):
        try:
            user, old_token = get_user_from_refresh_token(request)
            token_obj = UserToken.objects.filter(user=user, token=old_token, expired_at__gt=timezone.now()).first()
            if not token_obj:
                return Response({'error': 'User not found or token expired'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        token_obj.delete()
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        UserToken.objects.create(user=user, token=new_refresh_token, expired_at=timezone.now() + timedelta(days=7))

        secure_flag = not settings.DEBUG
        response = Response({
            'access_token': new_access_token,
            'refresh_token': new_refresh_token
        }, status=status.HTTP_200_OK)
        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            httponly=True,
            secure=secure_flag,
            samesite='None'
        )
        return response

class ServiceProviderListView(APIView):
    permission_classes = [permissions.AllowAny]

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

@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(APIView):
    def post(self, request: Request):
        token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')
        if not token:
            return Response({'error': 'Refresh token missing'}, status=status.HTTP_400_BAD_REQUEST)

        UserToken.objects.filter(token=token).delete()
        response = Response({'status': 'success', 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie(key='refresh_token')
        return response
