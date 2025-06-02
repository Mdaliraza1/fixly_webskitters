from django.db import models

class Service(models.Model):
    category = models.CharField(max_length=50)  
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category} - ₹{self.price}"
