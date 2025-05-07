from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import User

# Regex Validators
contact_regex = RegexValidator(regex=r'^[1-9]\d{9}$', message="Enter a valid 10-digit mobile number.")
email_regex = RegexValidator(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message="Enter a valid email address.")

# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[email_regex])
    password = serializers.CharField(write_only=True)

# Customer Registration Serializer
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    contact = serializers.CharField(validators=[contact_regex])
    email = serializers.EmailField(validators=[email_regex])

    # Override the username field to take the value of the email field
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'confirm_password',
                  'contact', 'gender']
        extra_kwargs = {
            'username': {'required': False}  # Make username optional
        }

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        # Check if the email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        # Check if the contact already exists
        if User.objects.filter(contact=data['contact']).exists():
            raise serializers.ValidationError("A user with this contact number already exists.")

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # Set username to be the same as email
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data, user_type='CUSTOMER')
        return user

# Service Provider Registration Serializer
class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    contact = serializers.CharField(validators=[contact_regex])
    email = serializers.EmailField(validators=[email_regex])

    # Override the username field to take the value of the email field
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'confirm_password',
                  'contact', 'gender', 'location', 'category']

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        # Check if the email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        # Check if the contact already exists
        if User.objects.filter(contact=data['contact']).exists():
            raise serializers.ValidationError("A user with this contact number already exists.")

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # Set username to be the same as email
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data, user_type='SERVICE_PROVIDER')
        return user

# User Serializer (added this for consistency in user-related views)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'contact', 'gender', 'location', 'category', 'user_type']

# User Update Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(validators=[contact_regex])

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'contact', 'gender', 'location', 'category']

# Password Change Serializer
class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
