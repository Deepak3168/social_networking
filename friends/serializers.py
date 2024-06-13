
from rest_framework import serializers
from .models import FriendRequest, Friend

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField()
    to_user = serializers.StringRelatedField()

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']


class FriendSerializer(serializers.ModelSerializer):
    friend_name = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ['id', 'friend_name']

    def get_friend_name(self, obj):
        user = self.context['request'].user
        if obj.user1 == user:
            return obj.user2.name
        else:
            return obj.user1.name
