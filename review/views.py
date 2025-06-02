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
        category = request.query_params.get('category')
        provider_id = request.query_params.get('provider_id')
        reviewer_id = request.query_params.get('reviewer_id')

        reviews = Review.objects.select_related('service_provider', 'reviewer')

        if category:
            reviews = reviews.filter(service_provider__category__iexact=category)
        if provider_id:
            reviews = reviews.filter(service_provider_id=provider_id)
        if reviewer_id:
            reviews = reviews.filter(reviewer_id=reviewer_id)

        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        if review.reviewer != request.user:
            return Response({"error": "You can only update your own review"}, status=status.HTTP_403_FORBIDDEN)

        data = {
            'rating': request.data.get('rating', review.rating),
            'comment': request.data.get('comment', review.comment),
            'service_provider': review.service_provider.id
        }

        serializer = ReviewCreateSerializer(review, data=data, partial=True, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Review updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
