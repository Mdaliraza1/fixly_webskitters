from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Get the JWT token from the request header
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == 'CUSTOMER')


class IsServiceProvider(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == 'SERVICE_PROVIDER')
