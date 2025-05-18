from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from registration.models import User
from dotenv import load_dotenv
from registration.authentication import decode_access_token
load_dotenv()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()

        if len(auth_header) != 2:
            raise AuthenticationFailed('Authorization header is malformed')

        try:
            token = auth_header[1].decode('utf-8')  # Decode bytes to str
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
