from rest_framework import permissions, status, exceptions
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta, timezone
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import User,UserToken
from .serializers import (
    CustomerRegistrationSerializer, ServiceProviderRegistrationSerializer,
    UserUpdateSerializer, ServiceProviderUpdateSerializer, UserSerializer
)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_access_token,decode_refresh_token

# Customer Registration View
class CustomerRegistrationView(APIView):
    def post(self, request):
        user=request.data
        print(f'User data received: {user}')
        if User.objects.filter(email=user['email']).exists():
           raise exceptions.APIException('Email already exists!')
        if User.objects.filter(username=user['username']).exists():
            raise exceptions.APIException('Username already exists!')
        if user['password'] != user['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        serializer = CustomerRegistrationSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Service Provider Registration View
class ServiceProviderRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ServiceProviderRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# User List View
class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

    def get(self, request):
        user = request.user
        is_admin = request.auth.get('is_admin', False)
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'is_admin': is_admin
        })

# User Detail View
class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    
    def get(self, request, id):
        """
        Retrieves details of a specific user by their ID.
        Allows staff to view any user's details, regular users can only view their own details.
        """
        try:
            user = User.objects.get(id=id)
            if request.user.is_staff or request.user == user:
                serializer = UserSerializer(user)
                return Response(serializer.data)
            return Response({"detail": "You do not have permission to view this user's details."}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# User Update View
class UserUpdateView(APIView):
    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
            if request.user.is_staff or request.user == user:
                serializer = UserUpdateSerializer(user, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "You do not have permission to update this user's details."}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#Provider update view
class ProviderUpdateView(APIView):
    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
            if request.user.is_staff or request.user == user:
                serializer = ServiceProviderUpdateSerializer(user, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "You do not have permission to update this user's details."}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# Login View with JWT
class LoginAPIView(APIView):
    def post(self, request: Request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid credentials')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentials')
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # here we are storing the refresh token of a specific user with an expiration date of 7 days
        UserToken.objects.create(
            user=user, 
            token=refresh_token, 
            expired_at = timezone.now() + timedelta(days=7)
        )

        response = Response()
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return response
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
    
# Service Provider List View with filters for category and location
class ServiceProviderListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Retrieves a list of service providers, with optional filters for category and location.
        """
        queryset = User.objects.filter(user_type='SERVICE_PROVIDER')
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        
        if category:
            queryset = queryset.filter(category=category)
        if location:
            queryset = queryset.filter(location=location)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(APIView):

    def post(self, request: Request):
        refresh_token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'detail': 'Refresh token missing'}, status=400)

        UserToken.objects.filter(token=refresh_token).delete()

        response: Response = Response({
            'status': 'success',
            'message': 'Logged out successfully'
        }, status=200)

        response.delete_cookie(key='refresh_token')
        return response
