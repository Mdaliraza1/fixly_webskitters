from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,UserToken
from .serializers import (
    CustomerRegistrationSerializer, ServiceProviderRegistrationSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, LoginSerializer, UserSerializer
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Customer Registration View
class CustomerRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handles the registration of a new customer.
        """
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Service Provider Registration View
class ServiceProviderRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handles the registration of a new service provider.
        """
        serializer = ServiceProviderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User List View
class UserListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Retrieves a list of all users.
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# User Detail View
class UserDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    
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
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, id):
        """
        Allows the authenticated user to update their details. 
        Staff can update any user's details, while regular users can only update their own.
        """
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

# Password Change View
class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Allows a user to change their password.
        """
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({"error": "Wrong current password."}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View with JWT
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handles user login and returns JWT tokens.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                })
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
