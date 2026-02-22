from django.shortcuts import render
from Profiles.models import UserProfile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Create your views here.

@api_view(['POST'])
def signup_views(request):
    username = request.data.get("username")
    email = request.data.get("email_id")
    first_name = request.data.get("firstname")
    last_name = request.data.get("lastname")
    info = request.data.get("info")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response(
            {"error": "Invalid data"},
            status=400
        )
    
    if UserProfile.objects.filter(email=email).exists():
        return Response(
            {"error": "Email Id alredy exists"},
            status=400
        )
    
    if UserProfile.objects.filter(username=username).exists():
        return Response(
            {"error": "Username Taken"},
            status=400
        )
    
    user = UserProfile.objects.create(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        info=info
    )

    user.set_password(password)

    user.save()

    return Response(
        {"message": "User Created sucessfully"},
        status=201
    )


@api_view(['POST'])
def login_views(request):
    username_email = request.data.get("username_email")
    password = request.data.get("password")

    if not username_email or not password:
        return Response({"error": "Invalid Data"}, status=400)
    
    # Use .get(), not .filter()
    try:
        if "@" in username_email:
            user = UserProfile.objects.get(email=username_email)
        else:
            user = UserProfile.objects.get(username=username_email)
    except UserProfile.DoesNotExist:
        return Response({"error": "User Does not exist"}, status=401)
    
    # Check password properly
    if not user.check_password(password):
        return Response({"error": "Incorrect Password"}, status=401)
    
    if not user.is_active:
        return Response({"error": "Account disabled"}, status=403)
    
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    return Response({
        "RefreshToken": str(refresh),
        "AccessToken": str(access)
    }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile_view(request):
    # request.user is automatically populated via the JWT token
    user = request.user 
    
    return Response({
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "info": user.info
    }, status=status.HTTP_200_OK)