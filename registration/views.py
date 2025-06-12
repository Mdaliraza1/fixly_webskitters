from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

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

class CustomerRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ServiceProviderRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ServiceProviderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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