from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterViewTestCase(TestCase):
    def test_register(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {"email": "test@example.com", "full_name": "Test", "password": "testpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.json())
