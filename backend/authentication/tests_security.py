from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User as AdminUser
from authentication.models import User
from authentication.serializers import UserSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from backend.asgi import application
from channels.db import database_sync_to_async
import json

class APISecurityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", auth_provider="manual", is_guest=False)
        self.token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_user_list_forbidden_for_jwt_user(self):
        """Regular users (even with valid JWT) should not see the user list."""
        url = "/api/auth/users/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_forbidden_for_anon(self):
        """Anonymous users should not see the user list."""
        self.client.credentials() # Clear creds
        url = "/api/auth/users/"
        response = self.client.get(url)
        # Depending on DRF settings, this might be 401 or 403.
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_serializer_excludes_sensitive_fields(self):
        """Check that the serializer strictly limits fields."""
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertIn("user_id", data)
        self.assertIn("username", data)
        self.assertNotIn("password", data)
        self.assertNotIn("is_superuser", data)

    def test_me_endpoint(self):
        """Test that /api/auth/me/ returns correct info for the logged in user."""
        url = "/api/auth/me/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)
        # permanent user validation
        self.assertEqual(response.data["identity_type"], "permanent")

        
class WebSocketSecurityTests(TransactionTestCase):
    async def test_websocket_rejects_no_token(self):
        communicator = WebsocketCommunicator(application, "ws/multiplayer/lobby/")
        connected, subprotocol = await communicator.connect()
        # Expecting close code 4003, so connect checks usually return False if it closes immediately
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_websocket_accepts_valid_token(self):
        user = await database_sync_to_async(User.objects.create)(username="wsuser", is_guest=True)
        # We need to manually construct the token because simplejwt needs 'user_id' which matches our model
        access_token = AccessToken()
        access_token["user_id"] = str(user.user_id)
        token = str(access_token)
        
        communicator = WebsocketCommunicator(application, f"ws/multiplayer/lobby/?token={token}")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
