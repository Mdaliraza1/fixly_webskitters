from rest_framework import serializers
from .models import Service
import re

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'category', 'description', 'price']

    def validate_category(self, value):
        value_lower = value.lower()
        valid_categories = ['plumber', 'carpenter', 'electrician', 'cleaning']
        if value_lower not in valid_categories:
            raise serializers.ValidationError("Category must be one of: Plumber, Carpenter, Electrician, Cleaning.")
        return value_lower.capitalize()

    def validate_price(self, value):
        value_str = str(value)
        if not re.match(r'^\d+(\.\d{1,2})?$', value_str):
            raise serializers.ValidationError("Enter a valid price (e.g., 100.00 or 50).")
        return value
