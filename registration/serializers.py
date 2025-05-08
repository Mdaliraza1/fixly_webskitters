import re
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import User

# Regex Validators
contact_regex = r'^[1-9]\d{9}$'
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
password_regex = r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9\s]).{8,}$'


# User Serializer
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        
        extra_kwargs = {        # This allows the password field to be included in requests but excluded from responses.
            'username': {'required': False},
            'password': {'write_only': True}
        }
    
class ProviderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'contact', 'gender', 'location', 'category'
        ]

    def get_location(self, obj):
        return obj.get_location_display() if obj.location else None

    def get_category(self, obj):
        return obj.category.name if obj.category else None
    
# Customer Registration Serializer
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)  # This is only for validation

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password', 'contact', 'gender']
        extra_kwargs = {
            'username': {'required': False},
            'password': {'write_only': True}  # Ensuring password is not included in the response
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
        if not re.match(password_regex, value):
            raise serializers.ValidationError("Password length should be 8 and contain UPPERCASE, lowercase, number, and Symbol")
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
        # Remove confirm_password before saving
        validated_data.pop('confirm_password', None)  # Remove confirm_password from validated data
        password = validated_data.pop('password', None)
        
        # Set username to be the same as email if not provided
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        
        # Set the user_type to 'USER' by default
        validated_data['user_type'] = 'USER'

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance



# Service Provider Registration Serializer
class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)  # This is only for validation
    category_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password',
                  'contact', 'gender', 'location', 'category','category_name']
        extra_kwargs = {
            'username': {'required': False},
            'password': {'write_only': True}  # Ensuring password is not included in the response
        }
    def get_category_name(self, obj):
        return obj.category.category if obj.category else None
    
    def validate_email(self, value):
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email address")
        return value

    def validate_contact(self, value):
        if not re.match(contact_regex, value):
            raise serializers.ValidationError("Enter valid 10 digit mobile number")
        return value

    def validate_password(self, value):
        if not re.match(password_regex, value):
            raise serializers.ValidationError("Password length should be 8 and contain UPPERCASE, lowercase, number, and Symbol")
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
        # Remove confirm_password before saving
        validated_data.pop('confirm_password', None)  # Remove confirm_password from validated data

        password = validated_data.pop('password', None)
        
        # Set username to be the same as email if not provided
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']

        # Set the user_type to 'SERVICE_PROVIDER' by default
        validated_data['user_type'] = 'SERVICE_PROVIDER'

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
        fields = ['username', 'first_name', 'last_name', 'contact', 'gender', 'location', 'category']

    def validate(self, data):
        # Ensure 'category' is provided for service providers
        if 'category' not in data and hasattr(self.instance, 'user_type') and self.instance.user_type == 'SERVICE_PROVIDER':
            raise serializers.ValidationError("Category is required for service providers.")
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
        # Ensure 'category' is provided for service providers
        if not data.get('category') and hasattr(self.instance, 'user_type') and self.instance.user_type == 'SERVICE_PROVIDER':
            raise serializers.ValidationError("Category is required for service providers.")
        return data
