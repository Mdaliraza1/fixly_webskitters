from django.db import models
from registration.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_bookings')
    date = models.DateField()
    time_slot = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)  # optional, helpful for tracking

    def __str__(self):
        return f"{self.user} booked {self.service_provider} on {self.date} at {self.time_slot}"

    class Meta:
        unique_together = ('service_provider', 'date', 'time_slot')
