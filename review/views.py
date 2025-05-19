from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Review
from .serializers import ReviewCreateSerializer, ReviewListSerializer
from registration.models import User, UserToken
from registration.authentication import decode_refresh_token

class CreateReviewView(APIView):
    def post(self, request):
        token = request.data.get("refresh_token") or request.COOKIES.get("refresh_token")
        if not token:
            return Response({"error": "Refresh token not provided"}, status=400)

        try:
            user_id = decode_refresh_token(token)
            user = User.objects.get(id=user_id)
            if not UserToken.objects.filter(user=user, token=token, expired_at__gt=timezone.now()).exists():
                return Response({"error": "Invalid or expired token"}, status=401)
        except Exception:
            return Response({"error": "Invalid token or user"}, status=401)

        serializer = ReviewCreateSerializer(data=request.data, context={"user": user})
        if serializer.is_valid():
            serializer.save(reviewer=user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ListReviewView(APIView):
    def get(self, request):
        provider_id = request.query_params.get('provider_id')
        reviewer_id = request.query_params.get('reviewer_id')

        reviews = Review.objects.all()
        if provider_id:
            reviews = reviews.filter(service_provider_id=provider_id)
        if reviewer_id:
            reviews = reviews.filter(reviewer_id=reviewer_id)

        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data)

class UpdateReviewView(APIView):
    def put(self, request, pk):
        token = request.data.get("refresh_token") or request.COOKIES.get("refresh_token")
        if not token:
            return Response({"error": "Refresh token not provided"}, status=400)

        try:
            user_id = decode_refresh_token(token)
            user = User.objects.get(id=user_id)
            if not UserToken.objects.filter(user=user, token=token, expired_at__gt=timezone.now()).exists():
                return Response({"error": "Invalid or expired token"}, status=401)
        except Exception:
            return Response({"error": "Invalid token or user"}, status=401)

        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)

        if review.reviewer != user:
            return Response({"error": "You can only update your own review"}, status=403)

        data = {
            'rating': request.data.get('rating', review.rating),
            'comment': request.data.get('comment', review.comment),
            'service_provider': review.service_provider.id  # Keep service provider constant
        }

        serializer = ReviewCreateSerializer(review, data=data, partial=True, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Review updated successfully'}, status=200)
        return Response(serializer.errors, status=400)
