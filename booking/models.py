
from django.db import models
from django.conf import settings
from datetime import time, timedelta, datetime

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    service_provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_bookings')
    date = models.DateField()
    time_slot = models.TimeField()

    def __str__(self):
        return f"{self.user} booked {self.service_provider} on {self.date} at {self.time_slot}"

    class Meta:
        unique_together = ('service_provider', 'date', 'time_slot')
