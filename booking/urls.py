
from django.urls import path
from .views import CreateBookingView, UserBookingsView, ServiceProviderBookingsView, AvailableSlotsView

urlpatterns = [
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('user/', UserBookingsView.as_view(), name='user-bookings'),
    path('provider/', ServiceProviderBookingsView.as_view(), name='provider-bookings'),
    path('slots/', AvailableSlotsView.as_view(), name='available-slots'),
]
