from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from Profiles.models import UserProfile, MetaProfileData
from Profiles.serializer import OTPVerifySerializer, SignupSerializer, LoginSerializer, MetaProfileSerializer, ThemeUpdateSerializer, CoreProfileUpdateSerializer, MetaProfileUpdateSerializer, ResetPasswordSerializer
from Profiles.services import sign_up_procedure, verify_otp_and_activate, resend_otp, login_procedure, update_theme, update_profile_meta_data, update_coredata
import logging
from rest_framework import status

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

    user = serializer.validated_data["user"]
    tokens = login_procedure(user)

    return Response(tokens)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile_view(request):
    user = request.user

    try:
        profile = MetaProfileData.objects.get(user=user)
    except MetaProfileData.DoesNotExist:
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = MetaProfileSerializer(profile)

    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_theme_view(request):
    user = request.user

    serializer = ThemeUpdateSerializer(data=request.data)
    if serializer.is_valid():
        theme = serializer.validated_data['theme']
        profile = update_theme(user, theme)
        return Response({
            "message": "The Theme is updated.",
            "updated_theme": profile.theme
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    core_fields = ['username', 'first_name', 'last_name']
    meta_fields = ['bio', 'banner', 'pfp', 'latitude', 'longitude', 'badges']

    core_data = {}
    meta_data = {}

    for key, item in data.items():
        if key in core_fields:
            core_data[key] = item
        if key in meta_fields:
            meta_data[key] = item
    
    response_data = {}

    if core_data:
        core_serializer = CoreProfileUpdateSerializer(
            data=core_data,
            context={'request': request},
        )
        if core_serializer.is_valid():
            updated_user = update_coredata(user, core_serializer.validated_data)
            response_data['core'] = core_serializer.validated_data
        else:
            return Response(core_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    if meta_data:
        meta_serializer = MetaProfileUpdateSerializer(
            data=meta_data,
            partial=True
        )
        if meta_serializer.is_valid():
            updated_meta = update_profile_meta_data(user, meta_serializer.validated_data)
            response_data['meta'] = meta_serializer.validated_data
        else:
            return Response(meta_serializer.errors, status=400)

    return Response({"message": "The data updated sucessfully!", "updated_data": response_data}, status=200)


