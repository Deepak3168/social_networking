from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friend

User = get_user_model()

class FriendRequestTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='test@user.com', name='testuser', password='testuser')
        self.user2 = User.objects.create_user(email='test2@user.com', name='testuser2', password='testuser2')

    def obtain_token(self, email, password):
        response = self.client.post(reverse('token_obtain_pair'), {'email': email, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access'], response.data['refresh']

    def test_send_and_accept_friend_request(self):
        user1_access_token, _ = self.obtain_token('test@user.com', 'testuser')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user1_access_token)
        response = self.client.post(reverse('friend-request'), {'to_user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friend Request Sent")
        print(response.data)

        friend_request = FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).first()
        self.assertIsNotNone(friend_request)
        self.assertEqual(friend_request.status, FriendRequest.PENDING)


        user2_access_token, _ = self.obtain_token('test2@user.com', 'testuser2')  

   
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user2_access_token)
        response = self.client.patch(reverse('update-friend-request', args=[friend_request.id]), {'status': FriendRequest.ACCEPTED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friend  Request Accepted")
        print(response.data)
  
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, FriendRequest.ACCEPTED)

        friend_instance = Friend.objects.filter(user1__in=[self.user1, self.user2], user2__in=[self.user1, self.user2]).first()
        self.assertIsNotNone(friend_instance)
        self.assertTrue(friend_instance.is_friends)

class FriendRequestRateLimitTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='test1@user.com', name='testuser1', password='testuser1')
        self.user2 = User.objects.create_user(email='test2@user.com', name='testuser2', password='testuser2')
        self.user3 = User.objects.create_user(email='test3@user.com', name='testuser3', password='testuser3')
        self.user4 = User.objects.create_user(email='test4@user.com', name='testuser4', password='testuser4')
        self.user5 = User.objects.create_user(email='test5@user.com', name='testuser5', password='testuser5')

    def obtain_token(self, email, password):
        response = self.client.post(reverse('token_obtain_pair'), {'email': email, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access'], response.data['refresh']

    def test_rate_limiting(self):
        user1_access_token, _ = self.obtain_token('test1@user.com', 'testuser1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user1_access_token)
        response = self.client.post(reverse('friend-request'), {'to_user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friend Request 1 Sent")
        print(response.data)
        response = self.client.post(reverse('friend-request'), {'to_user_id': self.user3.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friend Request 2 Sent")
        print(response.data)
        response = self.client.post(reverse('friend-request'), {'to_user_id': self.user4.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friend Request 3 Sent")
        print(response.data)
        response = self.client.post(reverse('friend-request'), {'to_user_id': self.user5.id})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        print("Friend Request 4 not Sent")
        print(response.data)
        self.assertEqual(response.data['error'], 'Rate limit exceeded. Please try again later.')




class FriendRequestsTests(APITestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(email='test1@user.com', name='testuser1', password='testuser1')
        self.user2 = User.objects.create_user(email='test2@user.com', name='testuser2', password='testuser2')
        self.user3 = User.objects.create_user(email='test3@user.com', name='testuser3', password='testuser3')

    def obtain_token(self, email, password):
        response = self.client.post(reverse('token_obtain_pair'), {'email': email, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access'], response.data['refresh']

    def test_friend_requests_list_and_acceptance(self):
        user2_access_token, _ = self.obtain_token('test2@user.com', 'testuser2')
        user3_access_token, _ = self.obtain_token('test3@user.com', 'testuser3')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user2_access_token)
        response = self.client.post(reverse('friend-request'), {'to_user_id': self.user1.id})
        print("Friend Request Sent")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user3_access_token)
        response = self.client.post(reverse('friend-request'), {'to_user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friend Request Sent")
        print(response.data)
        user1_access_token, _ = self.obtain_token('test1@user.com', 'testuser1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user1_access_token)
        response = self.client.get(reverse('friend-requests'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friend Requests")
        print(response.data)
        self.assertEqual(len(response.data), 2)
        from_users = [request['from_user'] for request in response.data]
        self.assertIn('testuser2', from_users)
        self.assertIn('testuser3', from_users)
        friend_requests = FriendRequest.objects.filter(to_user=self.user1)
        for fr in friend_requests:
            response = self.client.patch(reverse('update-friend-request', kwargs={'pk': fr.id}),{'status': FriendRequest.ACCEPTED})
            print("Friend Request Accepted")
            print(response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('friends-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Friends List")
        print(response.data)
        friend_names = [friend['friend_name'] for friend in response.data]
        self.assertIn('testuser2', friend_names)
        self.assertIn('testuser3', friend_names)
