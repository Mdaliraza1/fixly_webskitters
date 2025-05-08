from django.urls import path
from .views import CustomerRegistrationView, ServiceProviderRegistrationView,RefreshAPIView, UserAPIView, UserDetailView, UserUpdateView, ServiceProviderListView,ProviderUpdateView, LoginAPIView,LogoutAPIView

urlpatterns = [
    path('register/customer/', CustomerRegistrationView.as_view(), name='register_customer'),
    path('register/provider/', ServiceProviderRegistrationView.as_view(), name='register_provider'),

    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/',LogoutAPIView.as_view(),name="logout"),
    path('refresh/',RefreshAPIView.as_view(),name="token_refresh"),

    path('profile/', UserAPIView.as_view(), name='user_list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:id>/update/', UserUpdateView.as_view(), name='user_update'),

    path('providers/', ServiceProviderListView.as_view(), name='provider_list'),
    path('provider/update/<int:id>/', ProviderUpdateView.as_view(), name='provider-update'),
]
