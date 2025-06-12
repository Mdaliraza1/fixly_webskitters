from django.urls import path
from .views import (
    CustomerRegistrationView,
    ServiceProviderRegistrationView,
    RefreshView,
    UserAPIView,
    UserUpdateView,
    ProviderUpdateView,
    ServiceProviderListView,
    LoginView,
    LogoutView,
    create_admin_view
)
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-admin/', create_admin_view, name='create_admin'),
    path('register/customer/', CustomerRegistrationView.as_view(), name='register_customer'),
    path('register/provider/', ServiceProviderRegistrationView.as_view(), name='register_provider'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
    path('profile/', UserAPIView.as_view(), name='user_profile'),
    path('update/customer/', UserUpdateView.as_view(), name='update_customer'),
    path('update/provider/', ProviderUpdateView.as_view(), name='update_provider'),
    path('providers/', ServiceProviderListView.as_view(), name='provider_list'),
]
