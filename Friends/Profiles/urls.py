from django.urls import path
from Profiles import views

urlpatterns = [
    path('sign_up/', views.signup_views, name="user_signup")
]