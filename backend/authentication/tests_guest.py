from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import jwt
from django.conf import settings

class GuestAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Ensure we use the correct URL names from urls.py
        self.guest_url = reverse('guest') 
        self.me_url = reverse('me')

    def test_guest_login_flow(self):
        """
        Ensure a guest can login and access protected endpoints.
        """
        # 1. Login as Guest
        response = self.client.post(self.guest_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        data = response.json()
        self.assertIn('access', data)
        self.assertEqual(data['identity_type'], 'guest')
        
        token = data['access']
        user_id = data['user_id']
        
        # 2. Access Protected Endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        me_data = response.json()
        
        self.assertEqual(me_data['identity_type'], 'guest')
        self.assertEqual(me_data['user_id'], user_id)
        self.assertIn('guest_session', me_data)
