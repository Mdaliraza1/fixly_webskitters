from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    CustomerRegistrationView, ServiceProviderRegistrationView, UserListView,
    UserDetailView, UserUpdateView, PasswordChangeView, ServiceProviderListView,
    LoginView
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/customer/', CustomerRegistrationView.as_view(), name='register_customer'),
    path('register/provider/', ServiceProviderRegistrationView.as_view(), name='register_provider'),

    path('login/', LoginView.as_view(), name='login'),

    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),

    path('providers/', ServiceProviderListView.as_view(), name='provider_list'),
]
