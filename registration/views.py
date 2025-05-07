from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    CustomerRegistrationSerializer, ServiceProviderRegistrationSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, LoginSerializer, UserSerializer
)

class CustomerRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class ServiceProviderRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ServiceProviderRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        self.kwargs['id'] = self.request.user.id
        return super().get_object()

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        self.kwargs['id'] = self.request.user.id
        return super().get_object()

class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({"error": "Wrong current password."}, status=400)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully."})
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
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
            return Response({"error": "Invalid credentials"}, status=400)
        return Response(serializer.errors, status=400)

class ServiceProviderListView(generics.ListAPIView):
    queryset = User.objects.filter(user_type='SERVICE_PROVIDER')
    serializer_class = UserSerializer
    permission_classes=[permissions.AllowAny]
    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        location = self.request.query_params.get('location')
        if category:
            qs = qs.filter(category=category)
        if location:
            qs = qs.filter(location=location)
        return qs
    

