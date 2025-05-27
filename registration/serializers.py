from rest_framework import serializers
from .models import User

import re
from django.core.validators import RegexValidator


def validate_email_format(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise serializers.ValidationError("Invalid email format.")
    return email

def validate_password_strength(password):
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
    if not re.fullmatch(r'[6-9]\d{9}', contact):
        raise serializers.ValidationError("Contact number must be a valid 10-digit Indian mobile number.")
    return contact


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


# Provider Info Display Serializer
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
        return obj.category.category if obj.category else None


# Customer Registration Serializer
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password',
            'confirm_password', 'contact', 'gender'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        validate_email_format(value)
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_contact(self, value):
        validate_contact_format(value)
        if User.objects.filter(contact=value).exists():
            raise serializers.ValidationError("Contact number already in use.")
        return value

    def validate_password(self, value):
        return validate_password_strength(value)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if data['first_name'].lower() == data['last_name'].lower():
            raise serializers.ValidationError("First and last names cannot be the same.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        validated_data['username'] = validated_data['email']
        validated_data['user_type'] = 'CUSTOMER'

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Service Provider Registration Serializer
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
        extra_kwargs = {'password': {'write_only': True}}

    def get_category_name(self, obj):
        return obj.category.category if obj.category else None

    def validate_email(self, value):
        validate_email_format(value)
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_contact(self, value):
        validate_contact_format(value)
        if User.objects.filter(contact=value).exists():
            raise serializers.ValidationError("Contact number already in use.")
        return value

    def validate_password(self, value):
        return validate_password_strength(value)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if data['first_name'].lower() == data['last_name'].lower():
            raise serializers.ValidationError("First and last names cannot be the same.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        validated_data['username'] = validated_data['email']
        validated_data['user_type'] = 'SERVICE_PROVIDER'

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Customer Update Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'contact', 'gender', 'email']

    def validate(self, data):
        user = self.instance
        if user.user_type != 'CUSTOMER':
            raise serializers.ValidationError("Only customers can update this profile.")
        if 'email' in data:
            validate_email_format(data['email'])
            if User.objects.exclude(id=user.id).filter(email=data['email']).exists():
                raise serializers.ValidationError("Email already in use.")
        if 'contact' in data:
            validate_contact_format(data['contact'])
            if User.objects.exclude(id=user.id).filter(contact=data['contact']).exists():
                raise serializers.ValidationError("Contact number already in use.")
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# Service Provider Update Serializer
class ServiceProviderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'contact', 'gender', 'email', 'location', 'category']

    def validate(self, data):
        user = self.instance
        if user.user_type != 'SERVICE_PROVIDER':
            raise serializers.ValidationError("Only service providers can update this profile.")
        if 'email' in data:
            validate_email_format(data['email'])
            if User.objects.exclude(id=user.id).filter(email=data['email']).exists():
                raise serializers.ValidationError("Email already in use.")
        if 'contact' in data:
            validate_contact_format(data['contact'])
            if User.objects.exclude(id=user.id).filter(contact=data['contact']).exists():
                raise serializers.ValidationError("Contact number already in use.")
        category = data.get('category') or getattr(user, 'category', None)
        if not category:
            raise serializers.ValidationError("Category is required for service providers.")
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
