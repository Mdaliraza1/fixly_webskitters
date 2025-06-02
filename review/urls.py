from django.urls import path
from .views import CreateReviewView, ListReviewView

urlpatterns = [
    path('create/', CreateReviewView.as_view(), name='create-review'),
    path('all/', ListReviewView.as_view(), name='list-review'),
]
