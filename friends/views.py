from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friend
from .serializers import FriendRequestSerializer,FriendSerializer
from rest_framework import generics
from django.db.models import Q

User = get_user_model()

def rate_limit_by_ip(function):
    def _wrapped_view(self, request, *args, **kwargs):
        ip_address = request.META.get('REMOTE_ADDR')
        key = f'rate_limit_{ip_address}'
        count = cache.get(key, 0)
        if count >= 3:
            return Response({'error': 'Rate limit exceeded. Please try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(key, count + 1, 60)
        return function(self, request, *args, **kwargs)
    
    return _wrapped_view

class SendFriendRequest(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer
    pagination_class = None
    @method_decorator(cache_page(60))
    @method_decorator(vary_on_cookie)
    @rate_limit_by_ip
    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        try:
            to_user =  User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if to_user == request.user:
            return Response({'error': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        existing_request = FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists()
        if existing_request:
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        friend_request = FriendRequest(from_user=request.user, to_user=to_user)
        friend_request.save()
        return Response({'message': 'Friend request sent'}, status=status.HTTP_200_OK)

class UpdateFriendRequest(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    def patch(self, request, pk):
        try:
            friend_request = FriendRequest.objects.get(id=pk, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')  
        if new_status not in [FriendRequest.ACCEPTED, FriendRequest.REJECTED]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.status = new_status
        friend_request.save()

        if new_status == FriendRequest.REJECTED:
            friend_request.delete()

        return Response({'message': f'Friend request {new_status}'}, status=status.HTTP_200_OK)


class FriendRequests(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user).order_by('id')

class FriendsList(generics.ListAPIView):
    pagination_class = None
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Friend.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).order_by('id')