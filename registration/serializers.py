import re
from rest_framework import serializers
from .models import User

# Regex Validators
contact_regex = r'^[1-9]\d{9}$'
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {        
            'password': {'write_only': True}
        }

# Customer Registration Serializer
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)  # This is only for validation

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'confirm_password',
                  'contact', 'gender']
        extra_kwargs = {
            'username': {'required': False}  # Make username optional
        }

    def validate_email(self, value):
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email address")
        return value

    def validate_contact(self, value):
        if not re.match(contact_regex, value):
            raise serializers.ValidationError("Enter valid 10 digit mobile number")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        return value

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
        
        # Check if first_name and last_name are the same
        if data['first_name'].lower() == data['last_name'].lower():
            raise serializers.ValidationError("First name and last name cannot be the same.")
        
        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Set username to be the same as email if not provided
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

# Service Provider Registration Serializer
class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)  # This is only for validation

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'confirm_password',
                  'contact', 'gender', 'location', 'category']

    def validate_email(self, value):
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Only '@example.com' emails are allowed.")
        return value

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
        
        # Check if first_name and last_name are the same
        if data['first_name'].lower() == data['last_name'].lower():
            raise serializers.ValidationError("First name and last name cannot be the same.")
        
        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Set username to be the same as email if not provided
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

# User Update Serializer (for Customer)
class UserUpdateSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(validators=[contact_regex])
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'contact', 'gender']

    def validate(self, data):
        return data

# Service Provider Update Serializer (for Service Providers)
class ServiceProviderUpdateSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(validators=[contact_regex])
    location = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'contact', 'gender', 'location', 'category']

    def validate(self, data):
        if not data.get('category') and self.instance.user_type == 'SERVICE_PROVIDER':
            raise serializers.ValidationError("Category is required for service providers.")
        return data
