from django.urls import path
from Profiles import views

urlpatterns = [
    path('sign_up/', views.signup_views, name="user_signup"),
    path('login/', views.login_views, name="user_login"),
    path('profile/', views.get_profile_view, name="user_profile"),
    path('profile_update/', views.update_profile_view, name="update_user_profile")
]