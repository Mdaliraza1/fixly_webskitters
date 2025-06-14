from django.db import models
from registration.models import User
import random
import string

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETE', 'Complete'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_bookings')
    date = models.DateField()
    time_slot = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    booking_id = models.CharField(max_length=8, unique=True, blank=True, null=True, editable=False)

    def __str__(self):
        return f"{self.user} booked {self.service_provider} on {self.date} at {self.time_slot} - {self.status}"

    class Meta:
        unique_together = ('service_provider', 'date', 'time_slot')

    def save(self, *args, **kwargs):
        if not self.booking_id:
            while True:
                new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Booking.objects.filter(booking_id=new_id).exists():
                    self.booking_id = new_id
                    break
        super().save(*args, **kwargs)
