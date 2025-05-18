import jwt
from datetime import datetime, timedelta, timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from registration.models import User
import os
from dotenv import load_dotenv

load_dotenv()

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
        
        if not auth_header or auth_header[0].lower() != b'bearer':
            return None  # No token or wrong prefix, so no authentication here

        if len(auth_header) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(auth_header) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeError:
            raise AuthenticationFailed('Invalid token encoding.')

        user_id = decode_access_token(token)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')

        return (user, token)



def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=30),  # 30 seconds expiry
    }
    secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def decode_access_token(token):
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Access token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid access token')
    except Exception as e:
        raise AuthenticationFailed(f'Error decoding access token: {str(e)}')


def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(days=7),  # 7 days expiry
    }
    secret_key = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def decode_refresh_token(token):
    try:
        refresh_secret = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
        payload = jwt.decode(token, refresh_secret, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Refresh token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid refresh token')
    except Exception as e:
        raise AuthenticationFailed(f'Error decoding refresh token: {str(e)}')
