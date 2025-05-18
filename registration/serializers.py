import re
from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import User

# =======================
# Regex Validators
# =======================
contact_regex = r'^[1-9]\d{9}$'
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
password_regex = r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9\s]).{8,}$'

contact_validator = RegexValidator(
    regex=contact_regex,
    message='Enter a valid 10-digit mobile number starting from 1-9.'
)


# =======================
# General User Serializer
# =======================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


# =======================
# Provider Info Serializer
# =======================
class ProviderSerializer(serializers.ModelSerializer):
    location_display = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'contact', 'gender', 'location', 'location_display',
            'category', 'category_name'
        ]

    def get_location_display(self, obj):
        return obj.get_location_display() if obj.location else None

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None


# =======================
# Customer Registration Serializer
# =======================
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password',
            'confirm_password', 'contact', 'gender'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email address.")
        return value

    def validate_contact(self, value):
        if not re.match(contact_regex, value):
            raise serializers.ValidationError("Enter valid 10-digit mobile number.")
        return value

    def validate_password(self, value):
        if not re.match(password_regex, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, "
                "contain an UPPERCASE letter, a number, and a symbol."
            )
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already registered.")

        if User.objects.filter(contact=data['contact']).exists():
            raise serializers.ValidationError("Contact number already in use.")

        if data['first_name'].lower() == data['last_name'].lower():
            raise serializers.ValidationError("First and last names cannot be the same.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)

        validated_data['username'] = validated_data['email']
        validated_data['user_type'] = 'USER'

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


# =======================
# Service Provider Registration Serializer
# =======================
class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password',
            'confirm_password', 'contact', 'gender',
            'location', 'category', 'category_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def validate_email(self, value):
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email address.")
        return value

    def validate_contact(self, value):
        if not re.match(contact_regex, value):
            raise serializers.ValidationError("Enter valid 10-digit mobile number.")
        return value

    def validate_password(self, value):
        if not re.match(password_regex, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, "
                "contain an UPPERCASE letter, a number, and a symbol."
            )
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already registered.")

        if User.objects.filter(contact=data['contact']).exists():
            raise serializers.ValidationError("Contact number already in use.")

        if data['first_name'].lower() == data['last_name'].lower():
            raise serializers.ValidationError("First and last names cannot be the same.")

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)

        validated_data['username'] = validated_data['email']
        validated_data['user_type'] = 'SERVICE_PROVIDER'

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


# =======================
# Customer Update Serializer
# =======================
class UserUpdateSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(validators=[contact_validator])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'contact', 'gender', 'location']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# =======================
# Service Provider Update Serializer
# =======================
class ServiceProviderUpdateSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(validators=[contact_validator])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'contact', 'gender', 'category']

    def validate(self, data):
        user = self.instance
        category = data.get('category') or user.category
        if user.user_type == 'SERVICE_PROVIDER' and not category:
            raise serializers.ValidationError("Category is required for service providers.")
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

