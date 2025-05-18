from django.urls import path
from .views import (
    CustomerRegistrationView,
    ServiceProviderRegistrationView,
    RefreshAPIView,
    UserAPIView,
    UserUpdateView,
    ServiceProviderListView,
    ProviderUpdateView,
    LoginAPIView,
    LogoutAPIView,
)
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/customer/', CustomerRegistrationView.as_view(), name='register_customer'),
    path('register/provider/', ServiceProviderRegistrationView.as_view(), name='register_provider'),

    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('refresh/', RefreshAPIView.as_view(), name='token_refresh'),

    path('profile/', UserAPIView.as_view(), name='user_list'),

    path('update/customer/', UserUpdateView.as_view(), name='update_customer'),
    path('update/provider/', ProviderUpdateView.as_view(), name='update_provider'),

    path('providers/', ServiceProviderListView.as_view(), name='provider_list'),
]
