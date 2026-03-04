from django.urls import path
from Profiles import views

urlpatterns = [
    path("auth/signup/", views.signup, name="auth_signup"),
    path("auth/verify_otp/", views.verify_otp, name="auth_verify_otp"),
    path("auth/resend_otp/", views.resend_otp_view, name="auth_resend_otp"),
    path('auth/login/', views.login_views, name="user_login"),
    path('profile/', views.get_profile_view, name="user_profile"),
    path('profile_update_theme/', views. update_theme_view, name="update_theme"),
    path('profile_update/', views.update_profile, name="update_user_profile")
]