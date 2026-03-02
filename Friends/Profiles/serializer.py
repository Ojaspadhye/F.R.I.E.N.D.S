from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from Profiles.models import UserProfile



class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=5, max_length=100)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=50, required=False, default="")
    last_name = serializers.CharField(max_length=50, required=False, default="")
    password = serializers.CharField(min_length=8, write_only=True, validators=[validate_password])


    def validate_username(self, username):
        username = username.strip()
        if UserProfile.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("Username Taken")
        
        return username
    
    def validate_email(self, email):
        email = email.strip().lower()
        if UserProfile.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Account with Email exists")
        
        return email
    
    def to_validate_password(self, password):
        password = password.strip()
        validate_password(password)
        return password


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)

    def validate_email(self, email):
        return email.strip().lower()
    
    def validate_otp(self, otp):
        if not otp.isdigit():
            raise serializers.ValidationError("OTP is only numeric values")
        return otp


class LoginSerializer(serializers.Serializer):
    username_email = serializers.CharField(min_length=5, max_length=100, write_only=True)
    password = serializers.CharField(min_length=8, write_only=True, validators=[validate_password])

    user = None

    def validate_username_email(self, data):
        identifier = data.get('username_email').strip()
        password = data.get('password').strip()

        try:
            if '@' in identifier:
                identifier = identifier.lower()
                user = UserProfile.objects.get(email__iexact=identifier)
            else:
                user = UserProfile.objects.get(username__iexact=identifier)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_active:
            raise serializers.ValidationError("User inactive")
        
        self.user = user
        return user



