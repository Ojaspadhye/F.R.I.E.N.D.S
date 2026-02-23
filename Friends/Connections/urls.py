from django.urls import path
from Connections import views


urlpatterns = [
    path('sendrequest/', views.send_request, name="sending_request"),
    path('getfriends/', views.get_friends, name="get_friends"),
    path('get_pending_sent/', views.get_pending_sent, name="get_pending_sent"),
    path('get_recived_request/', views.get_pending_recived, name="get_recived_pending"),
    path('respond_request/', views.respond_request, name="Respond to request")
]