from django.shortcuts import render
from Profiles.models import UserProfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


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
        info=info,
        password=password
    )

    user.save()

    return Response(
        {"message": "User Created sucessfully"},
        status=201
    )


@api_view(['POST'])
def login_views(self, request):
    pass