import jwt
<<<<<<< HEAD
from rest_framework import exceptions
=======
import os
>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51
from datetime import datetime, timedelta, timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from registration.models import User
from dotenv import load_dotenv

load_dotenv()

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
<<<<<<< HEAD
        
        if len(auth_header) != 2:
            raise AuthenticationFailed('Authorization header is malformed.')
=======
        print("Auth header parts:", auth_header)

        if not auth_header or auth_header[0].lower() != b'bearer':
            raise AuthenticationFailed('Authorization header must start with Bearer')

        if len(auth_header) == 1:
            raise AuthenticationFailed('Token not found')
        elif len(auth_header) > 2:
            raise AuthenticationFailed('Authorization header must be Bearer token')

>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51
        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeDecodeError:
            raise AuthenticationFailed('Invalid token encoding.')
<<<<<<< HEAD
        try:
            user_id = decode_access_token(token)
=======

        try:
            user_id = decode_refresh_token(token)  # Using refresh token here
>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
        except Exception as e:
            raise AuthenticationFailed(f'Token validation error: {str(e)}')
<<<<<<< HEAD
        return (user, {'is_admin': user.is_superuser})  

=======

        return (user, {'is_admin': user.is_superuser})
>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51


def create_access_token(id):
    payload = {
        'user_id': id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=30),  # 30 seconds expiry
    }
    secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
<<<<<<< HEAD
    algorithm = "HS256"
=======
    algorithm = 'HS256'

>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def decode_access_token(token):
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'default_secret')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except Exception as e:
<<<<<<< HEAD
        raise exceptions.AuthenticationFailed(f'{str(e)}')
=======
        raise AuthenticationFailed(f'{str(e)}')
>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51


def create_refresh_token(user_id):
    payload = {
        'user_id': id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(days=7),  # 7 days expiry
    }
    secret_key = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret')
<<<<<<< HEAD
    algorithm = "HS256"
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
=======
    token = jwt.encode(payload, secret_key, algorithm="HS256")
>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51
    return token

def decode_refresh_token(token):
    try:
        refresh_secret = os.getenv('JWT_REFRESH_SECRET_KEY', 'default_secret') 
        payload = jwt.decode(token, refresh_secret, algorithms='HS256')
        print(f'payload: {payload}')
        return payload['user_id']
<<<<<<< HEAD
    except:
        raise exceptions.AuthenticationFailed('unauthenticated')
=======
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Refresh token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid refresh token.')

>>>>>>> 4c1e9cdc466586eb427255c2211e92e8da1daf51
