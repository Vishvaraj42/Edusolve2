import re
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'grade', 'phone_number', 'profile_picture', 'bio',
            'points', 'preferred_subjects', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'points', 'created_at', 'updated_at']

class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Confirm Password")
    phone_number = serializers.CharField(required=True) # Ensure phone is required
    
    class Meta:
        model = Student
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'grade', 'phone_number'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'grade': {'required': True},
        }

    def validate_password(self, value):
        """Feature 4: Enforce 1 Special, 1 Digit, 1 Upper, 1 Lower"""
        regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(regex, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character."
            )
        return value

    def validate_phone_number(self, value):
        """Feature 3: Basic valid mobile number check (e.g., +1234567890)"""
        regex = r'^\+?1?\d{9,15}$'
        if not re.match(regex, value):
            raise serializers.ValidationError("Please enter a valid mobile number (9-15 digits).")
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
            
        if Student.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
            
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        
        # Create the user, but set them as INACTIVE until they verify the OTP
        user = Student.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            grade=validated_data['grade'],
            phone_number=validated_data.get('phone_number', ''),
            is_active=False # The account cannot log in yet!
        )
        
        if hasattr(user, 'points'):
            user.points = 0
            
        user.save()
        return user

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'grade', 'phone_number', 'profile_picture', 'bio',
            'points', 'preferred_subjects', 'created_at',
        ]
        read_only_fields = ['id', 'username', 'points', 'created_at']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs