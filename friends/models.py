
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

User = get_user_model()

class FriendRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    REQUEST_STATUSES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=REQUEST_STATUSES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.from_user} to {self.to_user} ({self.status})"

    class Meta:
        unique_together = ['from_user', 'to_user']

class Friend(models.Model):
    user1 = models.ForeignKey(User, related_name='friends_set', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    is_friends = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1} and {self.user2} are friends"

    class Meta:
        unique_together = ['user1', 'user2']

@receiver(post_save, sender=FriendRequest)
def manage_friend_relationship(sender, instance, created, **kwargs):
    if not created:
        if instance.status == FriendRequest.ACCEPTED:
            user1, user2 = sorted([instance.from_user, instance.to_user], key=lambda user: user.id)
            Friend.objects.get_or_create(user1=user1, user2=user2, defaults={'is_friends': True})

