from django.urls import path
from .views import CreateReviewView, ListReviewView, UpdateReviewView

urlpatterns = [
    path('review/create/', CreateReviewView.as_view(), name='create-review'),
    path('review/all/', ListReviewView.as_view(), name='list-review'),
    path('review/update/<int:pk>/', UpdateReviewView.as_view(), name='update-review'),
]
