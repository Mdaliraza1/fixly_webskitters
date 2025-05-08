import jwt
from datetime import datetime, timedelta, timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication,get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from registration.models import User
import os
from dotenv import load_dotenv

load_dotenv()
  # Return the user and any extra data
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
        
        if len(auth_header) != 2:
            raise AuthenticationFailed('Authorization header is malformed')

        try:
            token = auth_header[1].decode('utf-8')  # Decode the token
            print(f'Token received from client: {token}')
        except UnicodeDecodeError:
            raise AuthenticationFailed('Invalid token encoding')

        try:
            user_id = decode_access_token(token)
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        except Exception as e:
            raise AuthenticationFailed(f'Token validation error: {str(e)}')
        return (user, {'is_admin': user.is_superuser}) 
    def decode_access_token(self, token):
        try:
            secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(f'{str(e)}')

# Token Creation Functions (You can keep them as utility functions outside of the class)

def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=30),  # Access token expiration (1 hour)
    }
    secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
    return jwt.encode(payload, secret_key, algorithm="HS256")

def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=7),  # Refresh token expiration (7 days)
        'iat': datetime.now(timezone.utc)
    }
    secret_key = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
    return jwt.encode(payload, secret_key, algorithm="HS256")
