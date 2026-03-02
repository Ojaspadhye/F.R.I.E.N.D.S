from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from Profiles.models import UserProfile
from Profiles.serializer import OTPVerifySerializer, SignupSerializer, LoginSerializer
from Profiles.services import sign_up_procedure, verify_otp_and_activate, resend_otp, login_procedure
import logging

# Create your views here.

logger = logging.getLogger(__name__)

class SignupThrottle(AnonRateThrottle):
    rate = "5/hour"

class OTPVerifyThrottle(AnonRateThrottle):
    rate = "10/hour"

class OTPResendThrottle(AnonRateThrottle):
    rate = "3/hour"

class LoginThrottle(AnonRateThrottle):
    rate = "15/hour"


@api_view(["POST"])
@throttle_classes([SignupThrottle])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sign_up_procedure(serializer.validated_data)
    return Response(
        {"message": "A verification code has been sent to your email."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@throttle_classes([OTPVerifyThrottle])
def verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    verify_otp_and_activate(
        email     = serializer.validated_data["email"],
        otp_input = serializer.validated_data["otp"],
    )
    
    return Response(
        {"message": "Account verified successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@throttle_classes([OTPResendThrottle])
def resend_otp_view(request):
    email = request.data.get("email", "").strip().lower()
    
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    resend_otp(email)

    return Response(
        {"message": "If this email is registered and unverified, a new code has been sent."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@throttle_classes([LoginThrottle])
def login_views(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_profile = serializer.user
    login_tokens = login_procedure(user_profile)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile_view(request):
    user = request.user
    return Response({
        "id":         user.id,
        "username":   user.username,
        "email":      user.email,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "info":       user.info,
    }, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile_view(request: Request) -> Response:
    user = request.user
    data = request.data

    allowed_fields = {
        "firstname": "first_name",
        "lastname":  "last_name",
        "info":      "info",
    }
    for request_key, model_field in allowed_fields.items():
        if request_key in data:
            setattr(user, model_field, data[request_key])

    if "username" in data:
        new_username = data["username"].strip().lower()
        if UserProfile.objects.filter(username__iexact=new_username).exclude(pk=user.pk).exists():
            return Response({"error": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        user.username = new_username

    user.save()
    return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)

