from django.db import models
from registration.models import User 

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_made')
    service_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reviewer', 'service_provider')
        ordering = ['created_at']

    def __str__(self):
        return f"Review by {self.reviewer.email} for {self.service_provider.first_name} - {self.rating}★"
