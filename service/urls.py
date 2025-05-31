from django.urls import path
from .views import ServiceListCreateView, ServiceRetrieveUpdateDestroyView

urlpatterns = [
    path('', ServiceListCreateView.as_view(), name='service-create'),
    path('<int:pk>/', ServiceRetrieveUpdateDestroyView.as_view(), name='service-retrieve-update-delete'),
]
