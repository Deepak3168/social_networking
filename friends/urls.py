
from django.urls import path
from .views import SendFriendRequest, UpdateFriendRequest,FriendRequests,FriendsList

urlpatterns = [
    path('friends/request/', SendFriendRequest.as_view(), name='friend-request'),
    path('friends/request/<int:pk>/', UpdateFriendRequest.as_view(), name='update-friend-request'),
    path('friends/requests/',FriendRequests.as_view(),name='friend-requests'),
    path('friends/list/',FriendsList.as_view(),name='friends-list')
]
