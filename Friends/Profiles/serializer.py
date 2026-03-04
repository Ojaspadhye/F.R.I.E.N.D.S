from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from Profiles.models import UserProfile, MetaProfileData



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
    password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("username_email").strip()
        password = attrs.get("password")

        try:
            if "@" in identifier:
                user = UserProfile.objects.get(email__iexact=identifier.lower())
            else:
                user = UserProfile.objects.get(username__iexact=identifier)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User inactive")

        attrs["user"] = user
        return attrs
    


from rest_framework import serializers

class CoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaProfileData
        fields = ["pfp", "banner"]  # images live on MetaProfileData


class MetaProfileSerializer(serializers.ModelSerializer):
    core_data = CoreProfileSerializer(source="user", read_only=True)
    image_profile = ProfileImageSerializer(source="*", read_only=True)
    class Meta:
        model = MetaProfileData
        fields = ["core_data", "image_profile", "bio", "friends_count", "badges", "theme"]
#    def get_friends_count(self, obj):  # Currently have commented due to incomplete state of friends or connections
#        return obj.user.friends.count() 



class ThemeUpdateSerializer(serializers.ModelSerializer):
    theme = serializers.ChoiceField(
        choices=[('light', 'light'), ('dark', 'dark')],
        required=True
    )

    class Meta:
        model = MetaProfileData
        fields = ['theme']


class CoreProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=5, max_length=100, required=False)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)

    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name']

    def validate_username(self, username):
        username = username.strip()

        user = self.context['request'].user

        if UserProfile.objects.filter(username__iexact=username).exclude(id=user.id).exists():
            raise serializers.ValidationError("Username is already taken")

        return username



class MetaProfileUpdateSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(max_length=300, required=False)
    banner = serializers.ImageField(required=False)
    pfp = serializers.ImageField(required=False)
    latitude = serializers.CharField(max_length=20, required=False)
    longitude = serializers.CharField(max_length=20, required=False)
    badges = serializers.ChoiceField(choices=[
        ('batman', 'batman'),
        ('joker', 'joker'),
        ('alfred', 'alfred'),
        ('nightwing', 'nightwing'),
        ('penguin', 'penguin'),
        ('riddler', 'riddler')
    ], required=False)

    class Meta:
        model = MetaProfileData
        fields = ['bio', 'banner', 'pfp', 'latitude', 'longitude', 'badges']


class ResetPasswordSerializer(serializers.Serializer):
    username_email = serializers.CharField(min_length=5, max_length=100, required=True)
    

    def validate(self, attrs):
        identifier = attrs.get("username_email").strip()
        password = attrs.get("password")

        try:
            if "@" in identifier:
                user = UserProfile.objects.get(email__iexact=identifier.lower())
            else:
                user = UserProfile.objects.get(username__iexact=identifier)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User inactive")

        attrs["user"] = user
        return attrs


