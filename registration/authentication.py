import jwt
import os
from datetime import datetime, timedelta, timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from registration.models import User
from dotenv import load_dotenv

load_dotenv()

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
        print("Auth header parts:", auth_header)

        if not auth_header or auth_header[0].lower() != b'bearer':
            raise AuthenticationFailed('Authorization header must start with Bearer')

        if len(auth_header) == 1:
            raise AuthenticationFailed('Token not found')
        elif len(auth_header) > 2:
            raise AuthenticationFailed('Authorization header must be Bearer token')

        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeDecodeError:
            raise AuthenticationFailed('Invalid token encoding.')

        try:
            user_id = decode_refresh_token(token)  # Using refresh token here
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
        except Exception as e:
            raise AuthenticationFailed(f'Token validation error: {str(e)}')

        return (user, {'is_admin': user.is_superuser})


def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=30),  # 30 seconds expiry
    }
    secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
    algorithm = 'HS256'

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def decode_access_token(token):
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except Exception as e:
        raise AuthenticationFailed(f'{str(e)}')


def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(days=7),  # 7 days expiry
    }
    secret_key = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def decode_refresh_token(token):
    try:
        refresh_secret = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
        payload = jwt.decode(token, refresh_secret, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Refresh token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid refresh token.')

