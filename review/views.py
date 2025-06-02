from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewCreateSerializer, ReviewListSerializer

class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListReviewView(APIView):
    permission_classes = []  

    def get(self, request):
        category_id = request.query_params.get('category')  # ID of Service
        provider_id = request.query_params.get('provider_id')
        reviewer_id = request.query_params.get('reviewer_id')

        reviews = Review.objects.select_related('service_provider', 'reviewer')

        if category_id:
            reviews = reviews.filter(service_provider__category=category_id)
        if provider_id:
            reviews = reviews.filter(service_provider_id=provider_id)
        if reviewer_id:
            reviews = reviews.filter(reviewer_id=reviewer_id)

        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




