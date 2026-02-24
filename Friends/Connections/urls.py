from django.urls import path
from Connections import views


urlpatterns = [
    path('sendrequest/', views.send_request, name="sendingrequest"),
    path('getfriends/', views.get_friends, name="getfriends"),
    path('get_pending_sent/', views.get_pending_sent, name="getpendingsent"),
    path('get_recived_request/', views.get_pending_recived, name="getrecivedpending"),
    path('respond_request/', views.respond_request, name="Respond to request")
]