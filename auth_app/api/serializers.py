"""Serializers for authentication endpoints."""
from rest_framework import serializers
from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation."""
    
    repeated_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, attrs):
        """Validate that password and repeated_password match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        """Create a new user with validated data."""
        validated_data.pop('repeated_password')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login validation."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)