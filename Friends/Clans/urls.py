from django.urls import path
from . import views

urlpatterns = [
    path("owned/", views.get_users_owned_clans, name="user-owned-clans"),
    path("joined/", views.get_user_joined_clans, name="user-joined-clans"),
    path("popular/", views.get_popular_clan, name="popular-clans"),
    path("by-name/", views.get_clan_by_name, name="clan-by-name"),
    path("by-age-range/", views.get_clan_by_agerange, name="clan-by-age-range"),
]