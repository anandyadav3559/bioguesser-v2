from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import jwt
import json

class GuestAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.guest_url = '/api/guest/' # Adjust if needed
        self.me_url = '/api/me/'       # Adjust if needed

    def test_guest_login_flow(self):
        # 1. Get Guest Token
        # Note: urls.py has path("guest/", GuestAuthView.as_view(), name="guest")
        # and include('authentication.urls') in main urls. 
        # I need to know the full path. Assuming /users/guest/ or similar based on app structure.
        # Let's check urls.py structure again.
        
        # Checking authentication/urls.py:
        # path('guest/', GuestAuthView.as_view(), name='guest')
        
        # Checking backend/urls.py (I haven't seen it yet, but standard practice is /api/ or similar)
        # I'll try to reverse 'guest' if names are set up, otherwise I'll guess /authentication/guest/
        
        url = reverse('guest') 
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        data = response.json()
        self.assertIn('access', data)
        self.assertEqual(data['identity_type'], 'guest')
        
        token = data['access']
        identity_id = data['identity_id']
        
        # 2. Access Protected Endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('me')) # Assuming 'me' is the name in urls.py
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        me_data = response.json()
        
        self.assertEqual(me_data['identity_type'], 'guest')
        self.assertEqual(me_data['identity_id'], identity_id)
        self.assertIn('guest_data', me_data)

