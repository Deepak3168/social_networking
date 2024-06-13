from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.users = []

        # Create 10 users
        for i in range(1, 18):
            user = User.objects.create_user(
                name=f'testuser{i}',
                email=f'test{i}@user.com',
                password=f'testuser{i}'
            )
            self.users.append(user)

        # URL for user login
        self.login_url = reverse('token_obtain_pair')  # Adjust this to your actual login URL name

        # Login testuser1
        response = self.client.post(self.login_url, {
            'email': 'test1@user.com',
            'password': 'testuser1'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_search_by_email(self):
        search_url = reverse('user-search')  # Adjust this to your actual search URL name
        response = self.client.get(search_url, {'q': 'test2@user.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'test2@user.com')

    def test_search_by_name_fragment(self):
        search_url = reverse('user-search')  # Adjust this to your actual search URL name
        response = self.client.get(search_url, {'q': 'testuser'}, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
