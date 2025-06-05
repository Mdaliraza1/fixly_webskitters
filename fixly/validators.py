from rest_framework import serializers
import re

def validate_rating(value):
    """Validate rating is between 1 and 5."""
    if not (1 <= value <= 5):
        raise serializers.ValidationError("Rating must be between 1 and 5.")
    return value

def validate_email_format(email):
    """Validate email format."""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise serializers.ValidationError("Invalid email format.")
    return email

def validate_password_strength(password):
    """Validate password meets security requirements."""
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise serializers.ValidationError("Password must include at least one uppercase letter.")
    if not re.search(r"[,\./\?;'!@#$%&*~]", password):
        raise serializers.ValidationError("Password must include at least one special character: ,./?;'!@#$%&*~")
    if not re.search(r'[a-z]', password):
        raise serializers.ValidationError("Password must include at least one lowercase letter.")
    if not re.search(r'\d', password):
        raise serializers.ValidationError("Password must include at least one digit.")
    return password

def validate_contact_format(contact):
    """Validate Indian mobile number format."""
    if not re.fullmatch(r'[6-9]\d{9}', contact):
        raise serializers.ValidationError("Contact number must be a valid 10-digit Indian mobile number.")
    return contact

def validate_service_provider(user):
    """Validate user is a service provider."""
    if user.user_type != 'SERVICE_PROVIDER':
        raise serializers.ValidationError("This action is only allowed for service providers.")
    return user

def validate_customer(user):
    """Validate user is a customer."""
    if user.user_type != 'CUSTOMER':
        raise serializers.ValidationError("This action is only allowed for customers.")
    return user

def validate_unique_review(reviewer, provider):
    """Validate one review per provider per customer."""
    from review.models import Review
    if Review.objects.filter(reviewer=reviewer, service_provider=provider).exists():
        raise serializers.ValidationError("You have already reviewed this service provider.")
    return True 
 